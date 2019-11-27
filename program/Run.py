import time
from KuhnGame import KuhnGame
from KuhnTest import KuhnTest
from KuhnTrainer import train

# Train a game tree from scratch. Theoretically, first player has game value -1/18.
train(iterations=10 ** 6, saveName="kt-10M")
# Continue training from a saved file
# continueTrain('kt-10Mp', 90*10**6, 'kt-200Mp')
kt = KuhnTest()
kt.read(filepath="kt-10M")
print(kt.gameValue())

# Play against trained game tree
game = KuhnGame()
game.read("kt-10M")
game.playAI(go_first=False, bankroll=0)
# game.read(filepath="kt-200Mp")
# game.playAI(goFirst=False, bankroll=0)
