from blist import sorteddict
import pickle, random
from KuhnNode import KuhnNode

class KuhnGame():
    AI: sorteddict

    def read(self, filepath: str):
        with open(filepath, 'rb') as f:
            self.AI = pickle.load(f)

    def playAI(self, go_first: bool, bankroll: int):
        cards = [1, 2, 3]
        random.shuffle(cards)
        print("You have: $" + str(bankroll))
        print("=============== Game start ===============\n"
              " Your card is: " + (str(cards[0]) if go_first else str(cards[1])))
        self.playAI(go_first, bankroll + self.gameRecursive(cards, '', go_first))

    def gameRecursive(self, cards, history: str, goFirst: bool):
        players = ["You", "AI"]
        plays = len(history)
        AI_turn = (plays % 2 == 1) if goFirst else plays % 2 == 0
        curr_player = plays % 2
        opponent = 1 - curr_player
        AI_card = str(cards[1]) if goFirst else str(cards[0])
        # Return payoff for terminal states
        if plays > 1:
            terminal_pass = history[plays - 1] == 'p'
            double_bet = history[plays - 2: plays] == 'bb'
            is_player_card_higher = cards[curr_player] > cards[opponent]
            if terminal_pass:
                if history == 'pp':
                    if is_player_card_higher:
                        print("AI had card " + AI_card + ". Game ended with history: " + history + ".\n" +
                              (players[1] if AI_turn else players[0]) + " won $1.")
                        return -1 if AI_turn else 1
                    else:
                        print("AI had card " + AI_card + ". Game ended with history: " + history + ".\n" +
                              (players[0] if goFirst else players[1]) + " won $1.")
                        return 1 if AI_turn else -1
                # History is 'pbp' or 'bp'
                else:
                    print("AI had card " + AI_card + ". Game ended with history: " + history + ".\n" +
                          (players[1] if AI_turn else players[0]) + " won $1.")
                    return -1 if AI_turn else 1
            # If terminal state does not end with pass it must be double bet.
            # elif double_bet:
            elif double_bet:
                if is_player_card_higher:
                    print("AI had card " + AI_card + ". Game ended with history: " + history + ".\n" +
                          (players[1] if AI_turn else players[0]) + " won $2.")
                    return -2 if AI_turn else 2
                else:
                    print("AI had card " + AI_card + ". Game ended with history: " + history + ".\n" +
                          (players[0] if AI_turn else players[1]) + " won $2.")
                    return 2 if AI_turn else -2

        info_set = str(cards[curr_player]) + history
        # Keep playing if not terminal state
        if AI_turn:
            AIStrategy = self.AI[info_set].getAverageStrategy()
            r = random.random()
            # AI passed
            if r < AIStrategy[0]:
                print("AI checked/passed.\n")
                return self.gameRecursive(cards, history + 'p', goFirst)
            else:
                print("AI bet $1.\n")
                return self.gameRecursive(cards, history + 'b', goFirst)

        else:
            # if cards[1] == 1:
            #     print("You passed.\n")
            #     return self.gameRecursive(cards, history + 'p', goFirst)
            # else:
            #     print("You bet $1.\n")
            #     return self.gameRecursive(cards, history + 'b', goFirst)
            bp = input("Your turn, enter 'b' for bet or 'p' for pass:\n")
            if bp == 'p':
                print("You passed.\n")
                return self.gameRecursive(cards, history + 'p', goFirst)
            elif bp == 'b':
                print("You bet $1.\n")
                return self.gameRecursive(cards, history + 'b', goFirst)
            else:
                return self.gameRecursive(cards, history, goFirst)

if __name__ == '__main__':
    game = KuhnGame()
    game.read('kt-3Mp')
    game.playAI(False, 0)
