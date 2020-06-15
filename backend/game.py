"""
Overall game class to track info related to turns and the board.
"""
from board import Board
import copy

class Game(object):

    def __init__(self, start_faction):
        self.old_board = Board()
        self.current_board = Board()
        self.faction = start_faction

    def __str__(self):
        return "{faction}'s turn{current}".format(
            faction = self.faction,
            current = self.current_board,
        )

    def reset_turn(self):
        self.current_board = copy.deepcopy(self.old_board)

    def end_turn(self):
        self.current_board.end_turn()
        self.old_board = copy.deepcopy(self.current_board)
        if self.faction == "Light":
            self.faction = "Dark"
        else:
            self.faction = "Light"

    def is_game_over(self):
        pass


if __name__ == "__main__":
    g = Game("Light")
    g.current_board.spells[0].cast()
    print(g)
    print('ENDING TURN')
    g.end_turn()
    print(g)
    g.current_board.spells[0].cast()
    print(g)
    print('ENDING TURN')
    g.end_turn()
    print(g)