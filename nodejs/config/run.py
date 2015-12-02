import click

from runutils import runbash, ensure_user, get_user_ids, run_daemon


USER_NAME, USER_ID, GROUP_NAME, GROUP_ID = get_user_ids('nodejs', 8080)
DEFAULT_USERNAME = USER_NAME or 'root'


@click.group()
def run():
    ensure_user(USER_NAME, USER_ID, GROUP_NAME, GROUP_ID)


@run.command()
@click.argument('user', default=DEFAULT_USERNAME)
def shell(user):
    runbash(user)


@run.command()
def start():
    params = ['nodejs', '/opt/src/tunnel/build.js']
    run_daemon(params, user=USER_NAME)


if __name__ == '__main__':
    run()
