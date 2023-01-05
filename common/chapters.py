import random


COMMANDS = ['cp', 'exec', 'ls', 'w', 'id', 'kill']

CHAPTERS = {
    # 1. largest response expected = uses chapters 19, 24, 26, 1, 23
    # cp needs path encoding
    'cp': [19, 24, 26, 1, 23],
    # 2. largest response expected = uses chapters 4, 2, 5, 14, 42
    # cp needs path encoding
    'exec': [4, 2, 5, 14, 42],
    # 3. largest response expected = uses chapters 44, 9, 3, 40, 11
    # cp needs path encoding
    'ls': [44, 9, 3, 40, 11],
    # 4. largest response expected = uses chapters 12, 13, 10, 6, 43, 7, 18, 20, 41, 27
    # used for path encoding
    'w': [12, 13, 10, 6, 43, 7, 18, 20, 41, 27],
    # smallest response expected
    # these files are too small for path encoding
    'id': [8, 15, 16, 17, 21, 22, 25, 28, 29, 30, 32, 33, 34, 35, 36, 37, 38, 39, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 58, 59, 60, 61, 62],
    # no response expected
    # these files are too small for path encoding
    'kill': [31, 57, 63, 64, 65],
}


def get_chapter_for_command(cmd):
    return random.choice(CHAPTERS[cmd])


def get_chapter_for_path_encoding():
    return random.choice(CHAPTERS['w'])


def get_command_for_chapter(chapter):
    for cmd in COMMANDS:
        if chapter in CHAPTERS[cmd]:
            return cmd
    return ''


def read_chapter(n):
    f = open(f'../bible/chapter_{n}.txt', 'r')
    text = f.read()
    f.close()
    return text
