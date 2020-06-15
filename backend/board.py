"""
Overall board class to store past and current game state.
"""

class Board(object):

    def __init__(self):
        self.rooms = []
        self.artworks = []
        self.spells = []
        self.players = []