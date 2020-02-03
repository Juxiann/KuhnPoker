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
        '''
        First output is return of player 0 given player 1 plays optimally.
        Second output is return of player 1 given player 0 plays optimally.
        Total exploitability is the negative of the sum of the two.
        :return:
        '''
        gt = self.best_response()
        output = [0, 0]
        for c in range(1, 4):
            output[0] += gt[str(c)]['ev'] / 3
            output[1] -= gt[str(c)]['br'] / 3
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

            curr_player = len(history) % 2
            other_player = 1 - curr_player
            childCards = {"1": ["2", "3"], "2": ["1", "3"], "3": ["1", "2"]}
            possibleCards = ["1", "2", "3"]
            if history == 'pb':
                x=1
            for next in ['p', 'b']:
                a = ['p', 'b'].index(next)
                if isTerminal(history + next):
                    for card in possibleCards:
                        if card + history == '1p':
                            x = 1
                        br_temp = 0
                        ev_temp = 0
                        npEV = 0
                        npBR = 0
                        for other in childCards[card]:
                            evCards = [int(card), int(other)] if curr_player == 1 else [int(other), int(card)]
                            brCards = [int(card), int(other)] if curr_player == 0 else [int(other), int(card)]
                            evRP = other + str(curr_player)
                            brRP = other + str(other_player)
                            evNextNode = KuhnNode()
                            evNextNode.infoSet = card + history + next
                            evCurrNode = self.nodeMap[other + history]
                            ev_temp += reachProb[evRP] * evCurrNode.getAverageStrategy()[a] * (
                                -evNextNode.returnPayoff(evCards))
                            npEV += reachProb[evRP]
                            brNextNode = KuhnNode()
                            brNextNode.infoSet = other + history + next
                            br_temp += reachProb[brRP] * (-brNextNode.returnPayoff(brCards))
                            npBR += reachProb[brRP]
                        if npEV != 0: ev_temp /= npEV
                        gameTree[card + history]['ev'] += ev_temp
                        if npBR != 0: br_temp /= npBR
                        if 'br' not in gameTree[card + history]:
                            gameTree[card + history]['br'] = br_temp
                        else: gameTree[card + history]['br'] = max(gameTree[card + history]['br'], br_temp)
                else:
                    # Update Reach Probabilities
                    newRP = {}
                    for card in possibleCards:
                        currNode = self.nodeMap[card + history]
                        if curr_player == 0:
                            newRP[card + '0'] = reachProb[card + '0'] * currNode.getAverageStrategy()[a]
                            newRP[card + '1'] = reachProb[card + '1']
                        else:
                            newRP[card + '0'] = reachProb[card + '0']
                            newRP[card + '1'] = reachProb[card + '1'] * currNode.getAverageStrategy()[a]
                    gameTree = traverseRecursive(self, history + next, newRP, gameTree)
                    for card in possibleCards:
                        ev_temp = 0
                        if 'br' not in gameTree[card + history]:
                            gameTree[card + history]['br'] = -gameTree[card + history + next]['ev']
                        else: gameTree[card + history]['br'] = max(gameTree[card + history]['br'], -gameTree[card + history + next]['ev'])
                        npEV = 0
                        for other in childCards[card]:
                            currNode = self.nodeMap[other + history]
                            evRP = other + str(curr_player)
                            npEV += reachProb[evRP]
                            ev_temp += reachProb[evRP] * currNode.getAverageStrategy()[a] * -gameTree[card + history + next]['br']
                        if npEV != 0: ev_temp /= npEV
                        gameTree[card + history]['ev'] += ev_temp
            return gameTree
        rp = {}
        RPList = ['10', '11', '20', '21', '30', '31']
        for card in RPList:
            rp[str(card)] = 1
        return traverseRecursive(self, '', rp, buildFullTree())

    # def best_response(self) -> dict:
    #     #     '''
    #     #     Returns the expected value of current infoSet, assuming opponents play by the best response.
    #     #     ev corresponds to the expected value of a
    #     #     node, calculated by the sum of expected value of child nodes, weighted
    #     #     by probability of choosing that action (assumes opponent plays by the best response.
    #     #     br corresponds to the value of a node, calculated assuming current player
    #     #     plays by the best response.
    #     #     '''
    #     #
    #     #     def traverseRecursive(self, history: str, reachProb: dict, gameTree: dict) -> dict:
    #     #         # NormalizingSum might be different for ev, br. might not need currReachProb
    #     #         curr_player = len(history) % 2
    #     #         other = 1 - curr_player
    #     #         childCards = {1: [2, 3], 2: [1, 3], 3: [1, 2]}
    #     #         possibleCards = [1, 2, 3]
    #     #         br_p = {'1': 0, '2': 0, '3': 0}
    #     #         br_b = {'1': 0, '2': 0, '3': 0}
    #     #
    #     #         for a in range(2):
    #     #             if a == 0:
    #     #                 if isTerminal(history + 'p'):
    #     #                     for card in possibleCards:
    #     #                         next = str(card) + history + 'p'
    #     #                         normalizingProb = 0
    #     #                         for childCard in childCards[card]:
    #     #                             evCards = [card, childCard] if curr_player == 0 else [childCard, card]
    #     #                             child_node = KuhnNode()
    #     #                             child_node = self.nodeMap[str(evCards[other]) + history + 'p']
    #     #                             gameTree[next]['ev'] += reachProb[str(evCards)] * child_node.returnPayoff(evCards)
    #     #                             normalizingProb += reachProb[str(evCards)]
    #     #                         if normalizingProb != 0:
    #     #                             gameTree[next]['ev'] /= normalizingProb
    #     #                 else:
    #     #                     newRP = {}
    #     #                     for card in possibleCards:
    #     #                         for childCard in childCards[card]:
    #     #                             cards = [card, childCard] if curr_player == 0 else [childCard, card]
    #     #                             curr_node = self.nodeMap[str(cards[curr_player]) + history]
    #     #                             newRP[str(cards)] = reachProb[str(cards)] * curr_node.getAverageStrategy()[0]
    #     #                     gameTree = traverseRecursive(self, history + 'p', newRP, gameTree)
    #     #                 for card in possibleCards:
    #     #                     curr = str(card) + history
    #     #                     br_p[curr] = -gameTree[curr + 'p']['ev']
    #     #             else:
    #     #                 if '1' + history + 'b' not in self.nodeMap:
    #     #                     for card in possibleCards:
    #     #                         normalizingProb = 0
    #     #                         next = str(card) + history + 'b'
    #     #                         for childCard in childCards[card]:
    #     #                             evCards = [card, childCard] if curr_player == 0 else [childCard, card]
    #     #                             child_node = KuhnNode()
    #     #                             child_node.infoSet = str(evCards[other]) + history + 'b'
    #     #                             gameTree[next]['ev'] += reachProb[str(evCards)] * child_node.returnPayoff(evCards)
    #     #                             normalizingProb += reachProb[str(evCards)]
    #     #
    #     #                         if normalizingProb != 0:
    #     #                             gameTree[next]['ev'] /= normalizingProb
    #     #                 else:
    #     #                     newRP = {}
    #     #                     for card in possibleCards:
    #     #                         for childCard in childCards[card]:
    #     #                             cards = [card, childCard] if curr_player == 0 else [childCard, card]
    #     #                             curr_node = self.nodeMap[str(cards[curr_player]) + history]
    #     #                             newRP[str(cards)] = reachProb[str(cards)] * curr_node.getAverageStrategy()[1]
    #     #                     gameTree = traverseRecursive(self, history + 'b', newRP, gameTree)
    #     #                 for card in possibleCards:0..
    #     #
    #     #
    #     #                     curr = str(card) + history
    #     #                     br_b[curr] = -gameTree[curr + 'b']['ev']
    #     #         for card in possibleCards:
    #     #             normalizingProb = 0
    #     #             curr = str(card) + history
    #     #             for selfCard in childCards[card]:
    #     #                 selfInfo = str(selfCard) + history
    #     #                 selfNode = self.nodeMap[selfInfo]
    #     #                 strategy = selfNode.getAverageStrategy()
    #     #                 evCards = [card, selfCard] if curr_player == 1 else [selfCard, card]
    #     #                 for next in ['p', 'b']:
    #     #                     if '1' + history + next not in self.nodeMap:
    #     #                         child_node = KuhnNode()
    #     #                         child_node.infoSet = str(evCards[other]) + history + next
    #     #                         gameTree[curr]['ev'] += \
    #     #                             reachProb[str(evCards)] * strategy[0 if next == 'p' else 1] * -child_node.returnPayoff(evCards)
    #     #                     else:
    #     #                         gameTree[curr]['ev'] += \
    #     #                             reachProb[str(evCards)] * strategy[0 if next == 'p' else 1] * -gameTree[curr + next]['br']
    #     #                 normalizingProb += reachProb[str(evCards)]
    #     #             if normalizingProb != 0:
    #     #                 gameTree[curr]['ev'] /= normalizingProb
    #     #         for card in possibleCards:
    #     #             curr = str(card) + history
    #     #             gameTree[curr]['br'] = max(br_p[curr], br_b[curr])
    #     #         return gameTree
    #     #
    #     #     rp = {}
    #     #     cardList = [[1, 2], [1, 3], [2, 1], [2, 3], [3, 1], [3, 2]]
    #     #     for card in cardList:
    #     #         rp[str(card)] = 1
    #     #     return traverseRecursive(self, '', rp, buildFullTree())

    def prune(self, threshold: str):
        for item in self.nodeMap:
            self.nodeMap[item].promising_branches = list(range(2))
            for i in range(2):
                if self.nodeMap[item].regretSum[i] < threshold:
                    self.nodeMap[item].promising_branches.remove(i)

def isTerminal(history: str) -> bool:
    return history == 'pp' or history == 'pbp' or history == 'pbb' or history == 'bp' or history == 'bb'

def buildFullTree():
    nodeMap = {}
    for card in range(1, 4):
        infoSet = str(card)
        for strategy in ['', 'p', 'b', 'pb']:
            IS = infoSet + strategy
            nodeMap[IS] = {'ev': 0}
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
    kt = KuhnTest()
    nodeMap = buildAverageStrategy()
    kt.nodeMap = nodeMap
    exp = kt.best_response()
    print(kt.gameValue())
    print(kt.exploitability())
    print(kt.best_response())
