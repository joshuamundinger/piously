"""
A Hex represents one of 28 hexes on the Piously board.

Hexes can be occupied by up to one Player or Artwork at a time,
and can have one aura.
"""
from backend.location import location_to_axial

class Hex(object):
    def __init__(self, room, location):
        self.room = room
        self.location = location
        self.aura = None
        self.occupant = None

    def __str__(self):
        return str(location_to_axial(self.location))
