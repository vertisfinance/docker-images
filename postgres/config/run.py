# coding: utf-8

import os
import re
import sys
import subprocess
import time
import signal
from contextlib import contextmanager
import hashlib

import click

# from runutils import (run_daemon, getvar, runbash, id, run_cmd, setuser,
#                       ensure_dir)
from runutils import (runbash, getvar, ensure_user, ensure_dir, run_cmd,
                      run_daemon, copyfile, substitute, get_user_ids,
                      setuser, Stopper)


# ####################################
# # CONFIGURATION: Edit if necessary #
# ####################################

USER_NAME, USER_ID, GROUP_NAME, GROUP_ID = get_user_ids('postgres', 5432)
PGDATA = getvar('PGDATA')
DB_PASSWORD = getvar('DB_PASSWORD')
CONFIG_FILE = getvar('CONFIG_FILE')
HBA_FILE = getvar('HBA_FILE')
SOCKET_DIR = getvar('SOCKET_DIR')
LOG_DIR = getvar('LOG_DIR', required=False)
BACKUP_DIR = getvar('BACKUP_DIR')
SEMAPHORE = getvar('SEMAPHORE', required=False)


def _init(stopper):
    ensure_dir(
        PGDATA_PARENT, owner='root', group='root', permission_str='777')
    ensure_dir(
        SOCKET_DIR, owner='root', group='root', permission_str='777')
    ensure_dir(
        LOG_DIR, owner='root', group='root', permission_str='777')
    ensure_dir(
        BACKUP_DIR, owner='root', group='root', permission_str='777')
    if SEMAPHORE_PARENT:
        ensure_dir(
            SEMAPHORE_PARENT, owner='root', group='root', permission_str='777')

    # copy config files
    copyfile(CONFIG_FILE, '/postgresql.conf',
             owner=USER_NAME, group=GROUP_NAME, permission_str='400')
    copyfile(HBA_FILE, '/pg_hba.conf',
             owner=USER_NAME, group=GROUP_NAME, permission_str='400')

    substitute('/postgresql.conf', {'SOCKET_DIR': SOCKET_DIR,
                                    'LOG_DIR': LOG_DIR})

    if not os.path.isdir(PGDATA):
        _initdb()
        _setpwd(USER_NAME, DB_PASSWORD)


# ##################################
# # UTILITY FUNCTIONS: do not edit #
# ##################################

PGDATA_PARENT = os.path.split(PGDATA)[0]
if SEMAPHORE:
    SEMAPHORE_PARENT = os.path.split(SEMAPHORE)[0]
else:
    SEMAPHORE_PARENT = None


start_postgres = ['postgres', '-c', 'config_file=%s' % '/postgresql.conf']


def psqlparams(command=None, database='postgres'):
    """Returns a list of command line arguments to run psql."""

    if command is None:
        return ['psql', '-d', database, '-h', SOCKET_DIR]
    else:
        return ['psql', '-d', database, '-h', SOCKET_DIR, '-c', command]


@contextmanager
def running_db():
    """
    Starts and stops postgres (if it is not running) so the block
    inside the with statement can execute command against it.
    """

    subproc = None
    if not os.path.isfile(os.path.join(PGDATA, 'postmaster.pid')):
        setpostgresuser = setuser(USER_NAME)
        subproc = subprocess.Popen(
            start_postgres,
            preexec_fn=setpostgresuser,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

        click.echo('Waiting for database to start...')
        time.sleep(1)

    try:
        yield
    finally:
        if subproc:
            subproc.send_signal(signal.SIGTERM)
            click.echo('Waiting for database to stop...')
            subproc.wait()


def _initdb():
    """Initialize the database."""

    run_cmd(['initdb'],
            user=USER_NAME,
            message='Initializing the database',
            printoutput=False)


def md5(username, password):
    tomd5 = '%s%s' % (password, username)
    tomd5 = tomd5.encode('utf-8')
    password = hashlib.md5()
    password.update(tomd5)
    password = password.hexdigest()
    return 'md5%s' % password


def _createuser(username, password):
    """Creates a user with the given password."""

    password = md5(username, password)
    sql = "CREATE USER %s WITH PASSWORD '%s'" % (username, password)

    with running_db():
        run_cmd(psqlparams(sql), 'Creating user', user=USER_NAME)


def _setpwd(username, password):
    """Sets the password for the given user."""

    password = md5(username, password)
    sql = "ALTER USER %s WITH PASSWORD '%s'" % (username, password)

    with running_db():
        run_cmd(psqlparams(sql), 'Setting password', user=USER_NAME,
                printoutput=True)


def _createdb(dbname, owner):
    """Creates a database."""

    sql = "CREATE DATABASE %s WITH ENCODING 'UTF8' OWNER %s"
    sql = sql % (dbname, owner)

    with running_db():
        run_cmd(psqlparams(sql), 'Creating database', user=USER_NAME)


def _createschema(schemaname, dbname, owner):
    """Creates a database."""

    sql = "CREATE SCHEMA %s AUTHORIZATION %s"
    sql = sql % (schemaname, owner)

    with running_db():
        run_cmd(psqlparams(sql, database=dbname),
                'Creating schema',
                user=USER_NAME)


def _backup(backupname, user, database):
    """Backs up the database with pg_dump."""

    # We have some restrictions on the backupname
    if re.match('[a-z0-9_-]+$', backupname) is None:
        click.secho('Invalid backupname.', fg='red')
        sys.exit(1)

    # The file must not exist
    filename = os.path.join(BACKUP_DIR, backupname)
    if os.path.isfile(filename):
        click.secho('File %s exists.' % filename, fg='red')
        sys.exit(1)

    params = ['pg_dump', '-h', SOCKET_DIR, '-O', '-x', '-U', user, database]

    with open(filename, 'w') as f, running_db():
        ret = subprocess.call(
            params, stdout=f, preexec_fn=setuser(USER_NAME))

    os.chown(filename, USER_ID, GROUP_ID)

    if ret == 0:
        click.secho('Successful backup: %s' % filename, fg='green')
    else:
        try:
            os.remove(filename)
        except:
            pass
        click.secho('Backup (%s) failed' % filename, fg='red')
        sys.exit(1)


def _restore(backupname, user, database, do_backup=True):
    """
    Recreatest the database from a backup file. Will drop the
    original database.
    Creates a backup if do_backup is True.
    """

    filename = os.path.join(BACKUP_DIR, backupname)
    if not os.path.isfile(filename):
        click.secho('File %s does not exist.' % filename, fg='red')
        sys.exit(1)

    with running_db():
        if do_backup:
            backupname = 'pre_restore_%s' % int(time.time())
            _backup(backupname, user, database)

        sql = 'DROP DATABASE %s;' % database

        run_cmd(psqlparams(sql),
                message='Dropping database %s' % database,
                user=USER_NAME)

        sql = ("CREATE DATABASE %s "
               "WITH OWNER %s "
               "ENCODING 'UTF8'" % (database, user))
        run_cmd(psqlparams(sql),
                message='Creating database %s' % database,
                user=USER_NAME)

        run_cmd(psqlparams() + ['-f', filename],
                message='Restoring',
                user=USER_NAME)


def _clear(confirm=True):
    """
    Removes PGDATA. Backup is recommended!
    """
    if not os.path.isdir(PGDATA):
        return

    if confirm and not click.confirm('Are you absolutely sure?'):
        return

    if os.path.isfile(os.path.join(PGDATA, 'postmaster.pid')):
        click.secho('Database is running. Stop it before clear.', fg='red')
        sys.exit(1)

    run_cmd(['rm', '-rf', PGDATA],
            message='Removing directory %s' % PGDATA)


# ######################################################################
# # COMMANDS                                                           #
# # Add your own if needed, remove or comment out what is unnecessary. #
# ######################################################################

@click.group()
def run():
    ensure_user(USER_NAME, USER_ID, GROUP_NAME, GROUP_ID)


@run.command()
@click.argument('user', default=USER_NAME)
def shell(user):
    runbash(user)


@run.command()
def init():
    _init(Stopper())


@run.command()
@click.option('--username', prompt=True)
@click.option('--password', prompt=True,
              hide_input=True, confirmation_prompt=True)
def createuser(username, password):
    _createuser(username, password)


@run.command()
@click.option('--username', prompt=True)
@click.option('--password', prompt=True,
              hide_input=True, confirmation_prompt=True)
def setpwd(username, password):
    _setpwd(username, password)


@run.command()
@click.option('--dbname', prompt=True)
@click.option('--owner', prompt=True)
def createdb(dbname, owner):
    _createdb(dbname, owner)


@run.command()
@click.option('--schemaname', prompt=True)
@click.option('--dbname', prompt=True)
@click.option('--owner', prompt=True)
def createschema(schemaname, dbname, owner):
    _createschema(schemaname, dbname, owner)


@run.command()
@click.option('--backupname', prompt=True)
@click.option('--user', prompt=True)
@click.option('--database', prompt=True)
@click.option('--do_backup', is_flag=True,
              prompt='Should we make backup?', default=False)
def restore(backupname, user, database, do_backup):
    _restore(backupname, user, database, do_backup)


@run.command()
@click.option('--backupname', prompt=True)
@click.option('--user', prompt=True)
@click.option('--database', prompt=True)
def backup(backupname, user, database):
    _backup(backupname, user, database)


@run.command()
def clear():
    _clear()


@run.command()
def start():
    run_daemon(start_postgres, user=USER_NAME, semaphore=SEMAPHORE,
               initfunc=_init)


if __name__ == '__main__':
    run()
