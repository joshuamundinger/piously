"""
One of the seven rooms of the temple.
"""
from backend.hex import Hex

class Room(object):
    def __init__(self, name, root, shape, a_spell, b_spell, relative_shape=True):
        # root is the location of the first hex of the room
        # shape is a list of vectors:
        #   the differentials between the root and other hexes in the room, if relative_shape
        #   the locations of other hexes, if not relative_shape

        self.root = root
        self.artwork = a_spell
        self.bewitchment = b_spell

        # create hexes
        if relative_shape:
            self.hexes = [Hex(self, root)] + [Hex(self, root + delta) for delta in shape]
        else:
            self.hexes = [Hex(self, root)] + [Hex(self, x) for x in shape]
        self.name = name

    def __str__(self):
        return self.name
