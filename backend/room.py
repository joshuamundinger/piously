"""
One of the seven rooms of the temple.
"""
from hex import Hex


class Room(object):
    def __init__(self, _root, _shape):
        #_root is the location of the first hex of the room
        #_shape is a list of vectors: 
        #   the differentials between the root and other hexes in the room

        self.root = _root
        #create hexes
        self.hexes = [Hex(_root)] + [Hex(_root + delta) for delta in _shape]
        
