import click

from runutils import runbash, ensure_user, getvar


USER_NAME = getvar('USER_NAME', required=False)

if USER_NAME is not None:
    USER_UID = int(getvar('USER_UID'))
    USER_GID = int(getvar('USER_GID', required=False) or USER_UID)
else:
    USER_UID, USER_GID = None, None

DEFAULT_USERNAME = USER_NAME or 'root'


@click.group()
def run():
    ensure_user(USER_NAME, USER_UID, gid=USER_GID)


@run.command()
@click.argument('user', default=DEFAULT_USERNAME)
def shell(user):
    runbash(user)


@run.command()
def start():
    pass


if __name__ == '__main__':
    run()
