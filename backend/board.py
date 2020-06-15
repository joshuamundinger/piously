"""
Overall board class to store past and current game state.
"""
from artwork import Artwork
from player import Player
from room import Room
from spell import Spell

class Board(object):

    def __init__(self):
        self.rooms = []
        self.artworks = [
            Artwork('Orange'),
        ]
        self.spells = [
            Spell('Overwork', '+1 Action for each adj. object', 'Orange'),
            Spell('Opportunist', 'Untap 1 action from 1 linked room', 'Orange'),
        ]
        self.players = [
            Player('Dark'),
            Player('Light'),
        ]
        self.actions = 3

    def __str__(self):
        return '\n***BOARD***\nactions:{actions}\nplayers:{players}\nspells:{spells}\nartworks:{artworks}\n***********\n'.format(
            actions = self.actions,
            players = display_list(self.players),
            spells = display_list(self.spells), 
            artworks = display_list(self.artworks), 
        )

    def end_turn(self):
        """Reset board values for start of new turn"""
        self.actions = 3
        [spell.untap() for spell in self.spells]


def display_list(list):
    return ''.join(['\n  {}'.format(item) for item in list])


if __name__ == "__main__":
    b = Board()
    b.spells[0].cast()
    print(b)
    b.end_turn()
    print(b)
