import re

f = open('whole.txt', 'r')
text = f.read()
f.close()

print('text[0:500]', text[0:500])

chapter = 1
iteration = 0
SIZE_PER_ITER = 100000
last_iter = len(text) / SIZE_PER_ITER
chapter_words = []


def add_newline_before_part(x):
    if bool(re.match('\d+:\d+', x)):
        return '\n\n' + x
    return x


def save_chapter(c, words):
    chapter_text = ' '.join(words)
    f = open(f'chapter_{c}.txt', 'w')
    f.write(chapter_text)
    f.close()


while True:
    if iteration >= last_iter:
        break

    print(f'Iteration {iteration}')

    iter_text = text[iteration * SIZE_PER_ITER:(iteration + 1) * SIZE_PER_ITER]\
        .lower()\
        .replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
    iter_words = [x for x in iter_text.split(' ') if len(x) > 0]

    for word in iter_words:
        if word == 'xxxxx':
            print(f'Saving chapter {chapter}')
            save_chapter(chapter, chapter_words)
            chapter_words.clear()
            chapter += 1
        else:
            chapter_words.append(add_newline_before_part(word))

    iteration += 1
