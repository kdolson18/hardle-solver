"""
Use an instance of the Problem class to represent a single problem with a known solution.
It provides feedback for each guess received based on that information.
"""

from random import randint
import pandas as pd
from config import wordLen, maxGuesses, words, validWord

def randWord(words):
    i = randint(0, len(words)-1)
    return words[i]

class Problem:
    _solution = ''
    solved = False
    failed = False
    
    def reset(self, solution=None):
        """
        Empties the guess history and chooses a new solution.
        """
        self._guesses = pd.DataFrame(index=range(maxGuesses), columns=['word', 'green', 'yellow'])
        self.solution = solution or randWord(words)
        self.solved = False
        self.failed = False
    
    def __init__(self, solution=None, verbose=True, *args, **kwargs):
        self.reset(solution)
        self.verbose = verbose
    
    @property
    def solution(self):
        return 'No cheating!'
    
    @solution.setter
    def solution(self, value):
        """
        Data validation when setting the solution
        """
        self._solution = validWord(value)
    
    @property
    def guesses(self):
        """
        Returns a dataframe containing the guess history and the results of the guesses.
        """
        guessFilter = self._guesses['word'].notna()
        return self._guesses[guessFilter]
    
    @property
    def remainingGuesses(self):
        """
        Returns a dataframe containing the remaining slots available for guesses.
        """
        remainingGuessFilter = self._guesses['word'].isna()
        return self._guesses[remainingGuessFilter]
    
    @guesses.setter
    def guesses(self, value):
        """
        Just making the syntax in self.guess() a little less awkward.
        """
        df = self.remainingGuesses
        assert not df.empty, 'Can\'t make another guess!'
        i = min(df.index)
        self._guesses.iloc[i] = value
    
    def guess(self, value):
        """
        Call this method to submit a guess.
        """
        guess = validWord(value)
        assert guess not in self.guesses['word'].values, "You've already guessed that word!"
        self.solved = guess == self._solution
        
        colours = self.checkColours(guess)
        self.guesses = (guess, colours['green'], colours['yellow'])
        self.failed = self.remainingGuesses.empty and not self.solved
        
        if self.verbose:
            print(self.guesses)
            if colours.get('green') == wordLen:
                print('Congratulations! You got it in {0} guesses.'\
                      .format(len(self.guesses.index)))
            if self.failed:
                print('You failed. Try harder next time!')
        
        return colours
    
    def checkColours(self, value):
        """
        Call this method to get the green and yellow counts for a guess.
        """
        isGreen = [self._solution[i] == value[i] for i in range(wordLen)]
        green = sum(isGreen)
        notGreen = [not x for x in isGreen]
        notGreenSol = [self._solution[i] if notGreen[i] else '' for i in range(wordLen)]
        yellowSol = ''.join(notGreenSol)
        yellow = 0
        for i in range(wordLen):
            letter = value[i]
            if letter in yellowSol and notGreen[i]:
                yellowSol = yellowSol.replace(letter, '?', count=1)
                yellow += 1
        return {'green': green, 'yellow': yellow}