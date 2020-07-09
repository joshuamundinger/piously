"""
One of the seven rooms of the temple.
"""
from backend.hex import Hex
import numpy as np

class Room(object):
    def __init__(self, name, root, shape, a_spell, b_spell, relative_shape=True):
        # root is the location of the first hex of the room if relative_shape
        # shape is a list of vectors:
        #   the differentials between the root and other hexes in the room, if relative_shape
        #   the locations of all hexes, if not relative_shape

        self.root = root
        self.artwork = a_spell
        self.bewitchment = b_spell

        # create hexes
        if relative_shape:
            self.hexes = [Hex(self, root)] + [Hex(self, root + delta) for delta in shape]
        else:
            # ignore
            self.hexes = [Hex(self, x) for x in shape]
        self.name = name

    def __str__(self):
        return self.name

    def rotate(self, increment):
        # rotate the room around the root (self.hexes[0]) counterclockwise through angle (2pi/6)*increment
        # this matrix rotates row vectors in the plane x1 + x2 + x3 = 0 through 2pi/6
        rotate_matrix = np.matrix([[ 0,0,-1],[-1,0,0],[0,-1,0]]).astype(int)
        for hex in self.hexes:
            hex.location = ((hex.location-self.hexes[0].location) * (rotate_matrix ** increment) + self.hexes[0].location).astype(int)

    def translate(self, displacement):
        # moves the whole room by displacement
        for hex in self.hexes:
            hex.location = hex.location + displacement

    def keyboard_movement(self, key):
        print('moving room based on keypress:{}'.format(key))
        if key == "left" or key == "ArrowLeft":
            self.translate(np.matrix([0,-1,1]))
        elif key == "right" or key == "ArrowRight":
            self.translate(np.matrix([0,1,-1]))
        elif key == "up" or key == "ArrowUp":
            self.translate(np.matrix([-1,0,1]))
        elif key == "down"or key == "ArrowDown":
            self.translate(np.matrix([1,0,-1]))
        elif key == ",":
            self.rotate(1)
        elif key == ".":
            self.rotate(int(-1))
