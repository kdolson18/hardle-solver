import re
from string import ascii_uppercase

wordLen = 5
maxGuesses = 10
regex = '^[A-Z]{' + str(wordLen) + '}$'

with open('words') as f:
    words = f.read().upper().split('", "')
words[0] = words[0][2:]
words[-1] = words[-1][:-3]

pool = ''.join(words)
frequencies = {letter: pool.count(letter) for letter in ascii_uppercase}
noDupes = list(filter(lambda x: len(set(x))==wordLen, words))


def validWord(value):
    assert isinstance(value, str), 'Value must be a string.'
    value = value.upper().strip()
    assert re.match(regex, value), f'Value must be {wordLen} letters.'
    assert value in words, 'Word not found in list.'
    return value


def makeGuessSet(n, i=None, guessSet=[], candidateSet=noDupes):
    assert bool(candidateSet), 'A word could not be chosen from candidateSet.'
    assert not i or isinstance(i, (int, list)), 'i must be an int or a list of ints'
    if isinstance(i, list):
        assert len(i) == n, 'len(i) must equal n'
    else:
        i = [i for x in range(n)]
    if n > 1:
        newGuess = candidateSet[i[0] or 0]
        newCandidateSet = list(filter(lambda x: not any([y in newGuess for y in x]), candidateSet))
        return makeGuessSet(n-1, i[1:], guessSet+[newGuess], newCandidateSet)
    else:
        return guessSet + [candidateSet[i[0] or 0]]