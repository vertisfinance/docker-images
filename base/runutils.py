# coding: utf-8

import os
import sys
import subprocess
import signal
import pwd
import shutil

import click


def getvar(name, default=None):
    """
    Returns the value of an environment variable.
    If the variable is not present and no default is given,
    raises an exception.
    """
    ret = os.environ.get(name, default)
    if not ret:
        raise Exception('Environment variable %s not set' % name)
    return ret


def ensure_dir(dir, owner=None, group=None, permission_str=None):
    """
    Checks the existence of the giver direcoty and creates it if not present.
    If `owner` is not present, root will own the newly created dir.
    If `group` is not present, the newly created dir's group will be root.
    """
    if not os.path.isdir(dir):
        os.makedirs(dir)

    if owner:
        subprocess.call(['chown', owner, dir])
    if group:
        subprocess.call(['chgrp', group, dir])
    if permission_str:
        subprocess.call(['chmod', permission_str, dir])


def ensure_user(username, uid, groupname=None, gid=None,
                unlock=False):
    """
    If `username` does not exist, we create one with uid.
    """
    if not groupname:
        groupname = username
    if not gid:
        gid = uid

    try:
        subprocess.call(['groupadd', '-g', str(gid), groupname])
    except:
        pass

    try:
        params = ['useradd',
                  '-u', str(uid),
                  '-g', str(gid),
                  '-s', '/bin/bash',
                  '-m', username]
        if unlock:
            params += ['-p', '*']
        subprocess.call(params)
    except:
        pass


def run_cmd(args, message=None, input=None, user=None):
    """
    Executes a one-off command. The message will be printed on terminal.
    If input is given, it will be passed to the subprocess.
    If user is given (as id or name) the process will run as the given user.
    """
    if message:
        click.echo(message + ' ... ')

    _setuser = setuser(user) if user else None

    if input is None:
        try:
            subprocess.check_output(
                args, stderr=subprocess.STDOUT, preexec_fn=_setuser)
        except subprocess.CalledProcessError as e:
            if message:
                click.secho('✘', fg='red')
            raise Exception(e.output) from None
        else:
            if message:
                click.secho('✔', fg='green')
    else:
        sp = subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=_setuser)
        out, err = sp.communicate(input)
        retcode = sp.wait()

        if retcode:
            if message:
                click.secho('✘', fg='red')
            raise Exception(err)
        else:
            if message:
                click.secho('✔', fg='green')


def run_daemon(params, stdout=None, stderr=None,
               signal_to_send=signal.SIGTERM,
               waitfunc=None, user=None,
               semafor=None, initfunc=None):
    """
    Runs the command as the given user (or root by default) in daemon mode
    and exits with it's returncode.
    Connects the given stdout, stderr, sends the specified signal to exit.

    The initialization of the container process will be blocked until
    `waitfunc` (if given) returns. If `waitfunc` is given it must accept
    an object and should return as soon as possible if object.stopped
    evaluates to True.

    After `waitfunc` returns, `initfunc` will run. Any container initialization
    can go here (create directories, db users, etc.) but should return as
    soon as object.stopped (must accept this parameter) is True.

    If semafor is provided it must be a path to a file. This file will
    be created after the main process is launched. Before exit the file
    will be deleted. Semafors can be used by other containers in their
    `waitfunc`. The presence of semafor does not mean the service is ready
    (ex. a database can accept connections), only that the process is started.
    A well designed `waitfunc` should first wait for the semafor, then test
    the service (ex. try to connect the db until it succeeds).
    """
    class Stopper(object):
        def __init__(self):
            self.stopped = False

    class SubprocessWrapper(object):
        def __init__(self):
            self.subprocess = None

    subprocess_wrapper = SubprocessWrapper()
    stopper = Stopper()

    def cleanup(signum, frame):
        """This will run when SIGTERM received."""
        if subprocess_wrapper.subprocess:
            subprocess_wrapper.subprocess.send_signal(signal_to_send)
        stopper.stopped = True

    signal.signal(signal.SIGTERM, cleanup)

    if waitfunc:
        waitfunc(stopper)

    if initfunc:
        initfunc(stopper)

    _setuser = setuser(user) if user else None
    if not stopper.stopped:
        sp = subprocess.Popen(
            params, stdout=stdout, stderr=stderr, preexec_fn=_setuser)
        subprocess_wrapper.subprocess = sp

        if semafor:
            open(semafor, 'w').close()

        waitresult = sp.wait()
    else:
        waitresult = 0

    try:
        os.remove(semafor)
    except:
        pass

    sys.exit(waitresult)


def setuser(user):
    """
    Returns a function that sets process uid, gid according to
    the given username.
    If the user does not exist, it raises an error.
    """
    pw = getpw(user)
    groups = list(set(os.getgrouplist(pw.pw_name, pw.pw_gid)))

    def chuser():
        os.setgroups(groups)
        os.setgid(pw.pw_gid)
        os.setuid(pw.pw_uid)
        os.environ['HOME'] = pw.pw_dir

    return chuser


def getpw(user):
    """
    Returns the pwd entry for a user given by uid or username.
    """
    if isinstance(user, int):
        return pwd.getpwuid(user)
    return pwd.getpwnam(user)


def substitute(filename, mapping):
    """
    Takes a file and substitutes all occurances of {{VARIABLE}}
    with values from mapping.
    """
    with open(filename, 'r') as f:
        content = f.read()

    for k, v in mapping.items():
        content = content.replace('{{%s}}' % k, v)

    with open(filename, 'w') as f:
        f.write(content)


def runbash(user):
    subprocess.call(['bash'], preexec_fn=setuser(user))


def merge_dir(src, dst, owner=None, group=None, permission_str=None):
    """
    Copy files and dirs from src to dst recursively.
    """
    assert all([os.path.isdir(src), os.path.isdir(dst)])

    for path, dirnames, filenames in os.walk(src):
        rel = os.path.relpath(path, start=src)
        pair = os.path.normpath(os.path.join(dst, rel))

        for d in dirnames:
            dirtocheck = os.path.join(pair, d)
            ensure_dir(dirtocheck, owner, group, permission_str)
            if not permission_str:
                shutil.copymode(os.path.join(path, d), dirtocheck)

        for f in filenames:
            srcfile = os.path.join(path, f)
            pairfile = os.path.join(pair, f)
            shutil.copy(srcfile, pairfile)
            if owner:
                subprocess.call(['chown', owner, pairfile])
            if group:
                subprocess.call(['chgrp', group, pairfile])
            if permission_str:
                subprocess.call(['chmod', permission_str, pairfile])
