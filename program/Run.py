import time
from KuhnGame import KuhnGame
from KuhnTest import KuhnTest
from KuhnTrainer import train, continueTrain

# Train a game tree from scratch, theoretical game value should be -1/18.
train(iterations=10 ** 6, saveName="kt-10M")
# Continue training from a saved file
# continueTrain('kt-10M', 90*10**6, 'kt-100M')
kt = KuhnTest()
kt.read(filepath="kt-3M")
print(kt.gameValue())

# Play against trained game tree
game = KuhnGame()
game.read("kt-10M")
game.playAI(go_first=False, bankroll=0)
# game.read(filepath="kt-200Mp")
# game.playAI(goFirst=False, bankroll=0)
