from common.chapters import read_chapter, CHAPTERS


def check_maximum_encoding_size_for_cmd(cmd):
    cmd = 'w' if cmd == 'path' else cmd
    chapters = CHAPTERS[cmd]
    min_size = 999999
    min_chapter = 0

    for chapter in chapters:
        text = read_chapter(chapter)
        words = text.split(' ')
        chapter_size = sum([1 for word in words if len(word) > 0 and word[0].isalpha()]) // 8 - 2
        if chapter_size < min_size:
            min_size = chapter_size
            min_chapter = chapter

    return min_size, min_chapter


def check_maximum_encoding_sizes():
    for cmd in ['cp', 'exec', 'ls', 'w', 'id', 'kill', 'path']:
        max_size, min_chapter = check_maximum_encoding_size_for_cmd(cmd)
        print(f'Maximum size for {cmd} is {max_size} ASCII characters (smallest chapter: {min_chapter})')


check_maximum_encoding_sizes()
