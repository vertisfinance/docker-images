import click

from runutils import (getvar, runbash, get_user_ids, ensure_user, copyfile,
                      substitute, run_daemon, ensure_dir, Stopper)


USER_NAME, USER_ID, GROUP_NAME, GROUP_ID = get_user_ids('nginx', 8080)
NGINX_CONF = getvar('NGINX_CONF')
MIME_TYPES = getvar('MIME_TYPES', default='nginx_mime.types')
STATIC_DIR = getvar('STATIC_DIR')
# make sure STATIC_DIR ends with '/'
STATIC_DIR = ('%s/' % STATIC_DIR).replace('//', '/')
DJANGO_UPSTREAM = getvar('DJANGO_UPSTREAM', default='django:8000')
UWSGI_PARAMS = getvar('UWSGI_PARAMS', required=False)
SOCKET_DIR = getvar('SOCKET_DIR', default='')


def _init(stopper):
    ensure_dir(STATIC_DIR,
               owner='root', group='root', permission_str='777')
    ensure_dir(
        SOCKET_DIR, owner='root', group='root', permission_str='777')

    # copy config files
    copyfile(NGINX_CONF, '/nginx.conf',
             owner=USER_NAME, group=GROUP_NAME, permission_str='400')
    copyfile(MIME_TYPES, '/nginx_mime.types',
             owner=USER_NAME, group=GROUP_NAME, permission_str='400')
    if UWSGI_PARAMS:
        copyfile(UWSGI_PARAMS, '/uwsgi_params',
                 owner=USER_NAME, group=GROUP_NAME, permission_str='400')

    substitute('/nginx.conf', {'USER_NAME': USER_NAME,
                               'STATIC_DIR': STATIC_DIR,
                               'DJANGO_UPSTREAM': DJANGO_UPSTREAM,
                               'SOCKET_DIR': SOCKET_DIR})


@click.group()
def run():
    ensure_user(USER_NAME, USER_ID, GROUP_NAME, GROUP_ID)


@run.command()
@click.argument('user', default='nginx')
def shell(user):
    runbash(user)


@run.command()
def init():
    _init(Stopper())


@run.command()
def start():
    params = ['nginx', '-c', '/nginx.conf']
    run_daemon(params, initfunc=_init)


if __name__ == '__main__':
    run()
