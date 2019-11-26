import random
from typing import *

PASS = 0
BET = 1
NUM_ACTIONS = 2
r = random.random()
class KuhnNode:
    def __init__(self):
        self.infoSet = ''
        self.regretSum = [0] * NUM_ACTIONS
        self.strategy = [0] * NUM_ACTIONS
        self.strategySum = [0] * NUM_ACTIONS

    def __str__(self):
        return self.infoSet + ' ' + ', '.join(str(e) for e in self.getAverageStrategy())

    # Update current information set mixed strategy through regret-matching
    def getStrategy(self, realization_weight: float) -> List[float]:
        normalizingSum = 0
        for a in range(NUM_ACTIONS):
            if self.regretSum[a] > 0:
                self.strategy[a] = self.regretSum[a]
            else:
                self.strategy[a] = 0
            normalizingSum += self.strategy[a]

        for a in range(NUM_ACTIONS):
            if normalizingSum > 0:
                self.strategy[a] /= normalizingSum
            else:
                self.strategy[a] = 1 / NUM_ACTIONS
            self.strategySum[a] += realization_weight * self.strategy[a]
        return self.strategy

    # Get average information set mixed strategy across all training iterations
    def getAverageStrategy(self) -> list:
        avgStrategy = [0] * NUM_ACTIONS
        normalizingSum = sum(self.strategySum)
        for a in range(NUM_ACTIONS):
            if normalizingSum > 0:
                avgStrategy[a] = self.strategySum[a] / normalizingSum
            else:
                avgStrategy[a] = 1 / NUM_ACTIONS
        for a in range(NUM_ACTIONS):
            if avgStrategy[a] < 0.01:
                avgStrategy[a] = 0
        normalizingSum = sum(avgStrategy)
        for a in range(NUM_ACTIONS):
            avgStrategy[a] /= normalizingSum
        return avgStrategy

    def returnPayoff(self, cards: List[int]) -> Optional[int]:
        history = self.infoSet[1:len(self.infoSet)]
        plays = len(history)
        curr_player = plays % 2
        opponent = 1 - curr_player

        # Return payoff for terminal states
        if plays > 1:
            terminalPass = history[plays - 1] == 'p'
            doubleBet = history[plays - 2: plays] == 'bb'
            isPlayerCardHigher = cards[curr_player] > cards[opponent]
            if terminalPass:
                if history == 'pp':
                    if isPlayerCardHigher:
                        return 1
                    else:
                        return -1
                # History is 'pbp' or 'bp'
                else:
                    return 1
            # If terminal state does not end with pass it must be double bet.
            # elif doubleBet:
            elif doubleBet:
                if isPlayerCardHigher:
                    return 2
                else:

                    return -2

