"""
Use an instance of the Solution class to represent a single problem with an unknown solution.
The Solution instance has an attached Problem instance that it tries to solve.
It narrows down the pool of potential solutions based on information received after each guess.
"""

import numpy as np, pandas as pd
from string import ascii_uppercase
from config import wordLen, words, validWord, frequencies
from problem import Problem

greenLabels = ['green_{0}'.format(x) for x in range(wordLen)]

def solve(func):
    """
    A decorator for a Solver method. The method should output a word.
    """
    def wrapped_func(solver):
        while not solver.problem.solved and not solver.problem.failed:
            word = func(solver)
            solver.guess(word)
    return wrapped_func


class Solver:
    
    # housekeeping
    def reset(self, solution=None):
        """
        Resets the solution pool and attaches a new problem.
        """
        self.solutionPool = pd.Series(words, index=words).index
        self.problem = Problem(solution=solution, verbose=self.verbose)
        
    def __init__(self, solution=None, verbose=True, rate=1, *args, **kwargs):
        self.verbose = verbose
        self.rate = rate
        self.reset(solution)
    
    
    # dataframes using self.solutionPool as their index
    @property
    def solutionPoolDf(self):
        """
        Returns a dataframe with the pool of eligible solutions as the index.
        Used primarily by self.eliminate()
        """
        columns = greenLabels + ['green', 'yellow']
        return pd.DataFrame(data = np.zeros((len(self.solutionPool), len(columns)), dtype=int),
                            index = self.solutionPool,
                            columns = columns,
                            )
    
    def frequencyDfMaker(self, freqDict):
        """
        Given a dictionary of weights for each letter, assigns a score to each word
        based on the sum of its letters' weights. Duplicated letters are only scored once.
        """
        df = self.solutionPoolDf
        df['score'] = 0
        for letter, freq in freqDict.items():
            df['score'] += df.index.str.contains(letter) * freq
        return df.sort_values('score', ascending=False)
    
    @property
    def staticFrequencyDf(self):
        """
        Makes a df with weighted scores based on the relative frequency of
        each letter in the overall word pool.
        """
        return self.frequencyDfMaker(frequencies)
    
    @property
    def frequencyDf(self):
        """
        Makes a df with weighted scores based on the relative frequency of
        each letter in the current solution pool.
        """
        pool = ''.join(self.solutionPool)
        freqDict = {letter: pool.count(letter) for letter in ascii_uppercase}
        return self.frequencyDfMaker(freqDict)
    
    
    # making guesses work
    def eliminate(self, value, colours):
        """
        Given a guess and the number of green and yellow letters in that guess,
        eliminates all words from the solution pool that cannot be the solution.
        """
        guess = validWord(value)
        df = self.solutionPoolDf
        greens = [df.index.str[i]==guess[i] for i in range(wordLen)]
        df['nogreen_sol'] = ''
        
        for i in range(wordLen):
            df['green_{0}'.format(i)] += greens[i]
            df['green'] += greens[i]
            df['nogreen_sol'] += df.index.str[i] * (1-df['green_{0}'.format(i)])
            
        df['nogreen_sol'] = df['nogreen_sol'].str.pad(wordLen, fillchar='*')
        
        for i in range(wordLen):
            letter = guess[i]
            containsYellowLetter = df['nogreen_sol'].str.contains(letter)
            notGreenLetter = df['green_{0}'.format(i)] < 1
            df.loc[containsYellowLetter & notGreenLetter,'yellow'] +=1
            df.loc[containsYellowLetter & notGreenLetter,'nogreen_sol'] = \
                df.loc[containsYellowLetter & notGreenLetter,'nogreen_sol']\
                    .str.replace(letter, '?', n=1)
                    
        correctGreen = df['green'] == colours.get('green')
        correctYellow = df['yellow'] == colours.get('yellow')
        possibilities = df[correctGreen & correctYellow]
        self.solutionPool = possibilities.index
        
        return possibilities
    
    def guess(self, word):
        """
        Passes a guess to the attached problem, then uses self.eliminate()
        to reduce the pool of potential solutions.
        """
        colours = self.problem.guess(word)
        self.eliminate(word, colours)
    
    
    # some easy solver examples I used to establish a performance baseline
    @solve
    def randomSolve(self):
        return np.random.choice(self.solutionPool)
    
    @solve
    def staticFrequencyMaxSolve(self):
        return self.staticFrequencyDf.index[0]
    
    @solve
    def frequencyMaxSolve(self):
        return self.frequencyDf.index[0]
    
    @solve
    def exponentialFrequencySolve(self):
        df = self.frequencyDf
        n = len(df.index)
        i = min(int(np.random.exponential(n/self.rate)), n-1)
        return df.index[i]
