import click

from runutils import runbash, ensure_user, getvar


USER_UID = int(getvar('USER_UID'))
USER_NAME = getvar('USER_NAME')


@click.group()
def run():
    ensure_user(USER_NAME, USER_UID)


@run.command()
@click.argument('user', default=USER_NAME)
def shell(user):
    runbash(user)


@run.command()
def start():
    pass


if __name__ == '__main__':
    run()
