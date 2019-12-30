import pickle, random
from KuhnNode import KuhnNode

class KuhnTest():
    nodeMap: dict

    def read(self, filepath: str):
        with open(filepath, 'rb') as f:
            self.nodeMap = pickle.load(f)

    # Plays the game against the strategy testNodeMap from a given history,
    # returns the utility of playing the simulated game.
    def test_play(self, testNodeMap: dict, history: str):
        cards = [1, 2, 3]
        random.shuffle(cards)
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

        # Keep playing if not terminal state
        infoSet = str(cards[curr_player]) + history
        if curr_player == 0:
            curr_strategy = self.nodeMap.get(infoSet).getAverageStrategy()
        else:
            curr_strategy = testNodeMap.get(infoSet).getAverageStrategy()
        r = random.random()
        if r < curr_strategy[0]:
            return -self.test_play(testNodeMap, history + 'p')
        else:
            return -self.test_play(testNodeMap, history + 'b')

    def gameValue(self):
        '''
        Each terminal node profit multiplied by its probability.
        :return:

        '''
        value = 0.
        cardList = [[1,2],[1,3],[2,1],[2,3],[3,1],[3,2]]

        def valueRecursive(self, infoSet: str) -> float:
            if infoSet not in self.nodeMap:
                node = KuhnNode()
                node.infoSet = infoSet
                return node.returnPayoff(cards)
            # Not a terminal node
            else:
                curr_player = (len(infoSet) - 1) % 2
                other = 1 - curr_player
                otherInfo = str(cards[other]) + infoSet[1:]
                strategy = self.nodeMap[infoSet].getAverageStrategy()
                value = 0
                for a in range(2):
                    if a == 0:
                        value += -valueRecursive(self, otherInfo + 'p') * strategy[a]
                    else:
                        value += -valueRecursive(self, otherInfo + 'b') * strategy[a]
                return value

        for cards in cardList:
            value += valueRecursive(self, str(cards[0])) / 6
        return value

    def exploitability(self) -> list:
        '''First output is player 0's best response, second is player 1's.'''
        gt = self.best_response()
        output = [0, 0]
        for c in range(1, 4):
            output[0] += gt[str(c)]['ev'] / 3
            output[1] += gt[str(c)]['br'] / 3
        return output

    def best_response(self) -> dict:
        '''
        Returns the expected value of current infoSet, assuming opponents play by the best response.
        ev corresponds to the expected value of a
        node, calculated by the sum of expected value of child nodes, weighted
        by probability of choosing that action (assumes opponent plays by the best response.
        br corresponds to the value of a node, calculated assuming current player
        plays by the best response.
        '''

        def traverseRecursive(self, history: str, reachProb: dict, gameTree: dict) -> dict:
            # NormalizingSum might be different for ev, br. might not need currReachProb
            curr_player = len(history) % 2
            other = 1 - curr_player
            childCards = {1: [2, 3], 2: [1, 3], 3: [1, 2]}
            possibleCards = [1, 2, 3]
            br_p = {'1': 0, '2': 0, '3': 0}
            br_b = {'1': 0, '2': 0, '3': 0}

            for a in range(2):
                if a == 0:
                    if '1' + history + 'p' not in self.nodeMap:
                        for card in possibleCards:
                            next = str(card) + history + 'p'
                            normalizingProb = 0
                            for childCard in childCards[card]:
                                evCards = [card, childCard] if curr_player == 0 else [childCard, card]
                                child_node = KuhnNode()
                                child_node.infoSet = str(evCards[other]) + history + 'p'
                                gameTree[next]['ev'] += reachProb[str(evCards)] * child_node.returnPayoff(evCards)
                                normalizingProb += reachProb[str(evCards)]
                            if normalizingProb != 0:
                                gameTree[next]['ev'] /= normalizingProb
                    else:
                        newRP = {}
                        for card in possibleCards:
                            for childCard in childCards[card]:
                                cards = [card, childCard] if curr_player == 0 else [childCard, card]
                                curr_node = self.nodeMap[str(cards[curr_player]) + history]
                                newRP[str(cards)] = reachProb[str(cards)] * curr_node.getAverageStrategy()[0]
                        gameTree = traverseRecursive(self, history + 'p', newRP, gameTree)
                    for card in possibleCards:
                        curr = str(card) + history
                        br_p[curr] = -gameTree[curr + 'p']['ev']
                else:
                    if '1' + history + 'b' not in self.nodeMap:
                        for card in possibleCards:
                            normalizingProb = 0
                            next = str(card) + history + 'b'
                            for childCard in childCards[card]:
                                evCards = [card, childCard] if curr_player == 0 else [childCard, card]
                                child_node = KuhnNode()
                                child_node.infoSet = str(evCards[other]) + history + 'b'
                                gameTree[next]['ev'] += reachProb[str(evCards)] * child_node.returnPayoff(evCards)
                                normalizingProb += reachProb[str(evCards)]

                            if normalizingProb != 0:
                                gameTree[next]['ev'] /= normalizingProb
                    else:
                        newRP = {}
                        for card in possibleCards:
                            for childCard in childCards[card]:
                                cards = [card, childCard] if curr_player == 0 else [childCard, card]
                                curr_node = self.nodeMap[str(cards[curr_player]) + history]
                                newRP[str(cards)] = reachProb[str(cards)] * curr_node.getAverageStrategy()[1]
                        gameTree = traverseRecursive(self, history + 'b', newRP, gameTree)
                    for card in possibleCards:
                        curr = str(card) + history
                        br_b[curr] = -gameTree[curr + 'b']['ev']
            for card in possibleCards:
                if history =='p':
                    x=1
                normalizingProb = 0
                curr = str(card) + history
                for selfCard in childCards[card]:
                    selfInfo = str(selfCard) + history
                    selfNode = self.nodeMap[selfInfo]
                    strategy = selfNode.getAverageStrategy()
                    evCards = [card, selfCard] if curr_player == 1 else [selfCard, card]
                    for next in ['p', 'b']:
                        if '1' + history + next not in self.nodeMap:
                            child_node = KuhnNode()
                            child_node.infoSet = str(evCards[other]) + history + next
                            gameTree[curr]['ev'] += \
                                reachProb[str(evCards)] * strategy[0 if next == 'p' else 1] * -child_node.returnPayoff(evCards)
                        else:
                            gameTree[curr]['ev'] += \
                                reachProb[str(evCards)] * strategy[0 if next == 'p' else 1] * -gameTree[curr + next]['br']
                    normalizingProb += reachProb[str(evCards)]
                if normalizingProb != 0:
                    gameTree[curr]['ev'] /= normalizingProb
            for card in possibleCards:
                curr = str(card) + history
                gameTree[curr]['br'] = max(br_p[curr], br_b[curr])
            return gameTree

        rp = {}
        cardList = [[1, 2], [1, 3], [2, 1], [2, 3], [3, 1], [3, 2]]
        for card in cardList:
            rp[str(card)] = 1
        return traverseRecursive(self, '', rp, buildFullTree())

    def prune(self, threshold: str):
        for item in self.nodeMap:
            self.nodeMap[item].promising_branches = list(range(2))
            for i in range(2):
                if self.nodeMap[item].regretSum[i] < threshold:
                    self.nodeMap[item].promising_branches.remove(i)

def buildFullTree():
    nodeMap = {}
    for card in range(1, 4):
        infoSet = str(card)
        for strategy in ['', 'p', 'b', 'pb', 'pp', 'pbp', 'pbb', 'bp', 'bb']:
            IS = infoSet + strategy
            nodeMap[IS] = {'ev': 0, 'br': 0}
    return nodeMap

def buildAverageStrategy():
    nodeMap = {}
    for card in range(1, 4):
        history = str(card)
        infoSet = history
        curr_node = KuhnNode()
        curr_node.infoSet = infoSet
        nodeMap[infoSet] = curr_node
        for strategy in ['p', 'b', 'pb']:
            infoSet = history + strategy
            curr_node = KuhnNode()
            curr_node.infoSet = infoSet
            nodeMap[infoSet] = curr_node
    return nodeMap

if __name__ == '__main__':
    # Read trained strategy
    import os
    my = KuhnTest()
    # my.nodeMap = buildAverageStrategy()
    my.read(os.getcwd() + '/kt-10M')
    for node in my.nodeMap.values():
        print(node)
    print(my.gameValue())
    gameTree = my.best_response()
    print(gameTree)
    print(my.exploitability())
    # print(sum(gameTree[str(c)] / 3 for c in range(1, 4)))
