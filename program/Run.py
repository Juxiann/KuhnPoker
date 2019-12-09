import time
from KuhnGame import KuhnGame
from KuhnTest import KuhnTest
from KuhnTrainer import train

# Train a game tree from scratch. Theoretically, first player has game value -1/18.
train(iterations=10 ** 6, saveName="kt-1M")
# Continue training from a saved file
# continueTrain('kt-1M', 9*10**6, 'kt-10M')
kt = KuhnTest()
kt.read(filepath="kt-1M")
print(kt.gameValue())

# Play against trained game tree
game = KuhnGame()
game.read("kt-1M")
game.playAI(go_first=False, bankroll=0)
