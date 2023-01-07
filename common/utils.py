from os import path, getcwd, unlink, listdir

from common.gist import pull_gist, push_gist, GIST_DIR_NAME

CHAT_FILE_NAME = '#chat.txt'
CHAT_FILE_PATH = path.join(GIST_DIR_NAME, CHAT_FILE_NAME)

CONTROLLER_NICK_NAME = 'LUKAS'


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
        with open(CHAT_FILE_PATH, 'r') as f:
            lines = [line.strip() for line in f.readlines() if len(line) > 0]
            last_lines = [line for line in lines if len(line) > 0][-count:]
            return [parse_msg(x) for x in last_lines]
    else:
        print('ERROR: The chat.txt file does not exist')
        exit(1)


def check_chat_file():
    return get_last_messages(1)[0][1]


def get_replies_to_msg_id(msg_id):
    pull_gist()

    if path.exists(CHAT_FILE_PATH):
        with open(CHAT_FILE_PATH, 'r') as f:
            lines = [line.strip() for line in f.readlines() if len(line) > 0]
            replies = [line for line in lines if line.find(f'): [REPLY {msg_id}] ') > -1]
            return [parse_msg(reply) for reply in replies]
    else:
        print('ERROR: The chat.txt file does not exist')
        exit(1)


def add_message(msg, nick_name, reply_to=None, attachment=None):
    pull_gist()
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

    return message_id


def read_attachment(attachment):
    f = open(path.join(GIST_DIR_NAME, attachment), 'r')
    text = f.read()
    f.close()
    return text


def reset_gist():
    pull_gist()

    folder = path.join(getcwd(), GIST_DIR_NAME)
    for filename in listdir(folder):
        if filename == '.git':
            continue

        try:
            unlink(path.join(folder, filename))
        except Exception:
            pass

    with open(CHAT_FILE_PATH, 'w') as f:
        f.write(f'[INIT] (1): Welcome to the online Bible bot, ask anything about the Bible!\n\n')

    push_gist()


get_last_messages(5)
