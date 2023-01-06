from os import system as call


GIST_URL = 'https://gist.github.com/ff1d1749b91389cc1f0fdb5c6d7ec580.git'
GIST_DIR_NAME = 'ff1d1749b91389cc1f0fdb5c6d7ec580'


def clone_gist():
    print('Cloning Gist from Git...', flush=True)
    call(f'git submodule add --force {GIST_URL}')


def pull_gist():
    print('Pulling Gist from Git...', flush=True)
    call(f'cd {GIST_DIR_NAME} && git fetch')
    call(f'cd {GIST_DIR_NAME} && git pull')


def push_gist():
    print('Pushing Gist to Git...', flush=True)
    call(f'cd {GIST_DIR_NAME} && git add . && git commit -m "msg" && git push')


def init_gist():
    print('Cloning Gist from Git...', flush=True)
    call(f'git submodule add --force {GIST_URL}')
    print('Updating Gist from Git...', flush=True)
    call(f'cd {GIST_DIR_NAME} && git fetch')
    call(f'cd {GIST_DIR_NAME} && git pull')
