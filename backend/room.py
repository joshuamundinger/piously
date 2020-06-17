"""
One of the seven rooms of the temple.
"""
from backend.hex import Hex

class Room(object):
    def __init__(self, root, shape, a_spell, b_spell):
        # root is the location of the first hex of the room
        # shape is a list of vectors: 
        #   the differentials between the root and other hexes in the room

        self.root = root

        # TODO: need a way to associate a Room with a Spell, so Rooms should have either spells or colors
        # added spells here, but could change it to colors instead
        self.artwork = a_spell
        self.bewitchment = b_spell

        # create hexes
        # TODO(josh): need to use vector addition
        self.hexes = [Hex(self, root)] + [Hex(self, root + delta) for delta in shape]


    def __str__(self):
        return ''.join(['\n  {}'.format(item) for item in self.hexes])
