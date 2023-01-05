from os import path
from subprocess import check_output

from common.gist import pull_gist, push_gist, GIST_DIR_NAME

CHAT_FILE_NAME = 'chat.txt'
CHAT_FILE_PATH = path.join(GIST_DIR_NAME, CHAT_FILE_NAME)

BOT_NICK_NAME = 'FORGY'
CONTROLLER_NICK_NAME = 'LUKAS'


def replace_newlines_with_spaces(txt):
    return txt.replace('\r\n', ' ').replace('\r', ' ').replace('\n', ' ')


def get_message_id_from_line(line):
    num_str = ''
    open_found = False
    for c in line:
        if c == '(':
            open_found = True
        elif c == ')':
            break
        elif open_found:
            num_str += c
    return int(num_str)


def check_chat_file():
    if path.exists(CHAT_FILE_PATH):
        last_message_line = check_output(f'grep -E "^\[.*\] \([[:digit:]]*\):" {CHAT_FILE_PATH} | tail -1', shell=True)
        return get_message_id_from_line(last_message_line.decode('utf-8').strip())
    else:
        print('ERROR: The chat.txt file does not exist')
        exit(1)


def parse_msg(line: str):
    line = line.strip()
    name, num, i, name_closed, num_opened = '', '', 1, False, False
    while True:
        c = line[i]
        if c == ']':
            name_closed = True
        elif c == '(':
            num_opened = True
        elif c == ')':
            break
        elif not name_closed:
            name += c
        elif num_opened:
            num += c
        i += 1
    return name, int(num), line[i+3:]


def get_last_commands(count):
    if path.exists(CHAT_FILE_PATH):
        last_lines = check_output(
            f'grep -E "^\[.*\] \([[:digit:]]*\):" {CHAT_FILE_PATH} | tail -{count}',
            shell=True
        ).decode('utf-8')
        return [parse_msg(x) for x in last_lines.replace('\r\n', '\n').replace('\r', '\n').split('\n') if len(x) > 0]
    else:
        print('ERROR: The chat.txt file does not exist')
        exit(1)


def add_message(msg, nick_name, reply_to=None):
    pull_gist()
    last_message_id = check_chat_file()

    with open(CHAT_FILE_PATH, 'a') as f:
        reply_str = f'[REPLY {reply_to}] ' if reply_to is not None else ''
        f.write(f'[{nick_name}] ({last_message_id + 1}): {reply_str}{msg}\n\n')

    push_gist()
