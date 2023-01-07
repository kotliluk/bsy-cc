from os import path
from subprocess import check_output

from common.gist import pull_gist, push_gist, GIST_DIR_NAME

CHAT_FILE_NAME = '#chat.txt'
CHAT_FILE_PATH = path.join(GIST_DIR_NAME, CHAT_FILE_NAME)

CONTROLLER_NICK_NAME = 'LUKAS'


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
    sender, msg_id, reply_id, attachment, name_closed, num_opened = '', '', None, None, False, False
    i = 1
    while True:
        c = line[i]
        if c == ']':
            name_closed = True
        elif c == '(':
            num_opened = True
        elif c == ')':
            break
        elif not name_closed:
            sender += c
        elif num_opened:
            msg_id += c
        i += 1
    msg = line[i+3:]

    if msg.startswith('[REPLY '):
        j = 7
        reply_id = ''
        while True:
            if msg[j] == ']':
                break
            reply_id += msg[j]
            j += 1
        reply_id = int(reply_id)
        msg = msg[j+2:]

    if msg.startswith('[ATTACH: '):
        j = 9
        attachment = ''
        while True:
            if msg[j] == ']':
                break
            attachment += msg[j]
            j += 1
        msg = msg[j+2:]

    return sender, int(msg_id), reply_id, attachment, msg


def get_last_messages(count):
    if path.exists(CHAT_FILE_PATH):
        try:
            last_lines = check_output(
                f'grep -E "^\[.*\] \([[:digit:]]*\):" {CHAT_FILE_PATH} | tail -{count}',
                shell=True
            ).decode('utf-8')
        except Exception:
            return []

        return [parse_msg(x) for x in last_lines.replace('\r\n', '\n').replace('\r', '\n').split('\n') if len(x) > 0]
    else:
        print('ERROR: The chat.txt file does not exist')
        exit(1)


def get_replies_to_msg_id(msg_id):
    pull_gist()
    print(flush=True)

    if path.exists(CHAT_FILE_PATH):
        try:
            raw_msgs = check_output(f'grep "): \[REPLY {msg_id}\] " {CHAT_FILE_PATH}', shell=True).decode('utf-8')
        except Exception:
            return []

        return [parse_msg(x) for x in raw_msgs.replace('\r\n', '\n').replace('\r', '\n').split('\n') if len(x) > 0]
    else:
        print('ERROR: The chat.txt file does not exist')
        exit(1)


def add_message(msg, nick_name, reply_to=None, attachment=None):
    pull_gist()
    print(flush=True)
    message_id = check_chat_file() + 1
    reply_str = f'[REPLY {reply_to}] ' if reply_to is not None else ''
    attachment_str = ''

    if attachment is not None:
        attachment_str = f'[ATTACH: {attachment["name"]}] '
        with open(path.join(GIST_DIR_NAME, attachment['name']), 'w') as f:
            f.write(attachment['content'])

    with open(CHAT_FILE_PATH, 'a') as f:
        f.write(f'[{nick_name}] ({message_id}): {reply_str}{attachment_str}{msg}\n\n')

    push_gist()
    print(flush=True)

    return message_id


def read_attachment(attachment):
    f = open(path.join(GIST_DIR_NAME, attachment), 'r')
    text = f.read()
    f.close()
    return text
