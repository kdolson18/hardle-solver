import re
from string import ascii_uppercase

wordLen = 5
maxGuesses = 10
regex = '^[A-Z]{' + str(wordLen) + '}$'

def validWord(value):
    assert isinstance(value, str), 'Value must be a string.'
    value = value.upper().strip()
    assert re.match(regex, value), 'Value must be {0} letters.'.format(wordLen)
    assert value in words, 'Word not found in list.'
    return value

with open('words') as f:
    words = f.read().upper().split('", "')
words[0] = words[0][2:]
words[-1] = words[-1][:-3]

pool = ''.join(words)
frequencies = {letter: pool.count(letter) for letter in ascii_uppercase}