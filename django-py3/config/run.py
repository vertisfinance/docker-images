import signal
import time
import os

import click
import psycopg2

from runutils import (run_daemon, runbash, ensure_dir, getvar, run_cmd,
                      copyfile, ensure_user, get_user_ids,
                      substitute, Stopper)


# ####################################
# # CONFIGURATION: Edit if necessary #
# ####################################


USER_NAME, USER_ID, GROUP_NAME, GROUP_ID = get_user_ids('django', 8000)
LISTEN_PORT = 8000
PG_SEMAPHORE = getvar('PG_SEMAPHORE', required=False)
UWSGI_CONF = getvar('UWSGI_CONF', required=False)
DB_USERNAME = getvar('DB_USERNAME')
DB_PASSWORD = getvar('DB_PASSWORD')
SOCKET_DIR = getvar('SOCKET_DIR')
CREATESUPERUSER_NAME = getvar('CREATESUPERUSER_NAME', required=False)
CREATESUPERUSER_EMAIL = getvar(
    'CREATESUPERUSER_EMAIL', required=CREATESUPERUSER_NAME)
CREATESUPERUSER_PASSWORD = getvar(
    'CREATESUPERUSER_PASSWORD', required=CREATESUPERUSER_NAME)
STATIC_DIR = getvar('STATIC_DIR')

CONN_STR = "host='%s' dbname='postgres' user='%s' password='%s'"
CONN_STR = CONN_STR % (SOCKET_DIR, DB_USERNAME, DB_PASSWORD)


################################################
# INIT: WILL RUN BEFORE ANY COMMAND AND START  #
# Modify it according to container needs       #
# Init functions should be fast and idempotent #
################################################


def _init(stopper):
    ensure_dir(STATIC_DIR,
               owner='root', group='root', permission_str='777')
    ensure_dir(
        SOCKET_DIR, owner='root', group='root', permission_str='777')

    if not stopper.stopped:
        run_cmd(['django-admin', 'migrate'],
                message='migrating',
                user='django',
                printoutput=True)

    if not stopper.stopped:
        run_cmd(['django-admin', 'collectstatic', '--noinput'],
                message='collectstatic',
                user='django',
                printoutput=True)

    # This is mainly for demonstartive purposes, but can be handy in
    # development
    if stopper.stopped:
        return

    import django
    django.setup()
    from django.contrib.auth.models import User

    if CREATESUPERUSER_NAME:
        try:
            User._default_manager.create_superuser(
                CREATESUPERUSER_NAME,
                CREATESUPERUSER_EMAIL,
                CREATESUPERUSER_PASSWORD)
        except:
            click.echo('Superuser exists')

    # copy config files
    if UWSGI_CONF:
        copyfile(UWSGI_CONF, '/uwsgi.conf',
                 owner=USER_NAME, group=GROUP_NAME, permission_str='400')

        substitute('/uwsgi.conf', {'SOCKET_DIR': SOCKET_DIR})


def _start_runserver():
    start = ['django-admin.py', 'runserver', '0.0.0.0:%s' % LISTEN_PORT]
    run_daemon(start, signal_to_send=signal.SIGINT, user=USER_NAME,
               waitfunc=_waitfordb, initfunc=_init)


def _start_uwsgi():
    """Starts the service."""
    start = ["uwsgi", "--ini", '/uwsgi.conf']
    run_daemon(start, signal_to_send=signal.SIGQUIT, user=USER_NAME,
               waitfunc=_waitfordb, initfunc=_init)


def _waitfordb(stopper):
    """
    Wait for the database to accept connections.
    """
    tick = 0.1
    intervals = 10 * [5] + 100 * [10]

    semaphore_ok = False
    for i in intervals:
        if PG_SEMAPHORE:
            click.echo('checking semafor ...')
            if os.path.isfile(PG_SEMAPHORE):
                semaphore_ok = True
            else:
                click.echo('no semafor yet')
                semaphore_ok = False
        else:
            semaphore_ok = True

        if semaphore_ok:
            click.echo('checking connection ...')
            try:
                psycopg2.connect(CONN_STR)
            except:
                click.echo('could not connect yet')
            else:
                return

        for w in range(i):
            if stopper.stopped:
                return
            time.sleep(tick)


######################################################################
# COMMANDS                                                           #
# Add your own if needed, remove or comment out what is unnecessary. #
######################################################################

@click.group()
def run():
    ensure_user(USER_NAME, USER_ID, GROUP_NAME, GROUP_ID)


@run.command()
def init():
    _init(Stopper())


@run.command()
@click.argument('user', default=USER_NAME)
def shell(user):
    runbash(user)


@run.command()
def start():
    if UWSGI_CONF:
        _start_uwsgi()
    else:
        _start_runserver()


if __name__ == '__main__':
    run()
