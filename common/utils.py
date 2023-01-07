from os import path, getcwd, unlink, listdir

from common.gist import pull_gist, push_gist, GIST_DIR_NAME

CHAT_FILE_PREFIX = path.join(GIST_DIR_NAME, '#CHAT')

BOT_SLEEP_TIME = 5
CONTROLLER_NICK_NAME = 'MAIN'


def parse_msg(line: str, sender):
    line = line.strip()
    msg_id, reply_id, attachment = '', None, None
    i = 1
    while True:
        c = line[i]
        if c == ')':
            break
        else:
            msg_id += c
        i += 1
    msg = line[i+3:]

    if msg.startswith('[REPLY '):
        j = 7
        reply_id = ''
        reading_nums = True
        while True:
            if msg[j] == ' ':
                reading_nums = False
            elif msg[j] == ']':
                break
            elif reading_nums:
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


def get_user_file(user):
    return f'{CHAT_FILE_PREFIX}-{user}.txt'


def get_last_messages(user, count):
    file_path = get_user_file(user)
    if path.exists(file_path):
        with open(file_path, 'r') as f:
            lines = [line.strip() for line in f.readlines() if len(line) > 0]
            last_lines = [line for line in lines if len(line) > 0][-count:]
            return [parse_msg(x, user) for x in last_lines]
    else:
        print(f'ERROR: The {file_path} file does not exist')
        return []


def check_chat_file(user):
    ret = get_last_messages(user, 1)
    return 0 if len(ret) == 0 else ret[0][1]


def get_user_from_chat_name(chat_name):
    return chat_name[6:-4]


def get_replies_to_msg_id(msg_id, user):
    pull_gist()
    all_replies = []

    folder = path.join(getcwd(), GIST_DIR_NAME)
    for filename in listdir(folder):
        print('filename', filename, flush=True)
        if not filename.startswith('#CHAT') or filename == get_user_file(CONTROLLER_NICK_NAME):
            continue

        with open(path.join(folder, filename), 'r') as f:
            lines = [line.strip() for line in f.readlines() if len(line) > 0]
            print('lines', lines)
            replies = [line for line in lines if line.find(f'): [REPLY {msg_id} {user}] ') > -1]
            all_replies += [parse_msg(reply, get_user_from_chat_name(filename)) for reply in replies]

    return all_replies


def add_message(msg, nick_name, reply_to=None, attachment=None):
    message_id = check_chat_file(nick_name) + 1
    reply_str = f'[REPLY {reply_to["msg_id"]} {reply_to["user"]}] ' if reply_to is not None else ''
    attachment_str = ''

    pull_gist()

    if attachment is not None:
        attachment_str = f'[ATTACH: {attachment["name"]}] '
        with open(path.join(GIST_DIR_NAME, attachment['name']), 'w') as f:
            f.write(attachment['content'])

    with open(get_user_file(nick_name), 'a') as f:
        f.write(f'({message_id}): {reply_str}{attachment_str}{msg}\n\n')

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

    with open(get_user_file(CONTROLLER_NICK_NAME), 'w') as f:
        f.write(f'[INIT] (1): Welcome to the online Bible bot, ask anything about the Bible!\n\n')

    push_gist()
