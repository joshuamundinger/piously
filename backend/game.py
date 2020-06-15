"""
Overall game class to track info related to turns and the board.
"""
from board import *

class Game(object):

    def __init__(self, start_faction):
        self.old_board = Board()
        self.current_board = Board()
        self.faction = start_faction


    def rest_turn(self):
        self.current_board = self.old_board

    def end_turn(self):
        self.old_board = self.current_board
        if self.faction == "Light":
            self.faction = "Dark"
        else:
            self.faction = "Light"

    def is_game_over(self):
        pass


if __name__ == "__main__":
    g = Game("Light")
    print(g.faction)
    g.end_turn()
    print(g.faction)