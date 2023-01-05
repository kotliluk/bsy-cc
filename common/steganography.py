def to_binary(msg):
    binary_length = bin(len(msg))[2:].rjust(16, '0')
    binary_msg = ''
    for c in msg:
        binary_msg += bin(ord(c))[2:].rjust(8, '0')
    return binary_length + binary_msg


def from_binary(msg):
    binary_length = msg[0:16]
    binary_msg = msg[16:]
    length = int(binary_length, 2)
    decoded_msg = ''

    if len(binary_msg) < length * 8:
        print('STEGANOGRAPHY ERROR: text does not contain the whole message')

    for i in range(length):
        cur_bin_part = binary_msg[i*8:(i+1)*8]
        decoded_msg += chr(int(cur_bin_part, 2))

    return decoded_msg


def encode_to_text(msg, text):
    """
    Returns the given text with the message encoded in it and the used length (in characters)
    """

    binary_msg = to_binary(msg)

    words = text.split(' ')
    new_words = []
    last_used_word = 0
    processed = 0

    for i, word in enumerate(words):
        if len(word) == 0 or not word[0].isalpha() or processed == len(binary_msg):
            new_words.append(word)
            continue
        if binary_msg[processed] == '1':
            new_words.append(word.capitalize())
        else:
            new_words.append(word)

        processed += 1
        if processed == len(binary_msg):
            last_used_word = i

    used_len = sum([len(x) for x in new_words[0:last_used_word+1]]) + last_used_word

    if processed < len(binary_msg):
        print('STEGANOGRAPHY ERROR: text is not long enough to hide the whole message')
        used_len = len(text)

    return ' '.join(new_words), used_len


def decode_from_text(text):
    words = text.split(' ')
    alpha_words = []

    for word in words:
        if len(word) > 0 and word[0].isalpha():
            alpha_words.append(word)

    binary_msg = ''

    for word in alpha_words:
        if word[0].isupper():
            binary_msg += '1'
        else:
            binary_msg += '0'

    return from_binary(binary_msg)
