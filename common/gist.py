from os import system as call
from time import sleep


GIST_URL = 'https://gist.github.com/ff1d1749b91389cc1f0fdb5c6d7ec580.git'
GIST_DIR_NAME = 'ff1d1749b91389cc1f0fdb5c6d7ec580'


def pull_gist():
    call(f'cd {GIST_DIR_NAME} && git fetch -q')
    call(f'cd {GIST_DIR_NAME} && git pull -q')
    print(flush=True)


def push_gist():
    r = call(f'cd {GIST_DIR_NAME} && git add . && git commit -m "msg" -q && git push -q')

    while r != 0:
        # retry in case of parallel git process
        sleep(2)
        r = call(f'cd {GIST_DIR_NAME} && git push -q')

    print(flush=True)


def init_gist():
    print('Cloning Gist from Git...', flush=True)
    call(f'git submodule add --force {GIST_URL}')
    pull_gist()
