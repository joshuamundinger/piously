"""
A Hex represents one of 28 hexes on the Piously board.

Hexes can be occupied by up to one Player or Artwork at a time,
and can have one aura.
"""
from backend.location import location_to_axial
from backend.errors import InvalidMove

class Hex(object):
    def __init__(self, room, location):
        self.room = room
        self.location = location
        self.aura = None
        self.occupant = None

    def __str__(self):
        return str(location_to_axial(self.location))

    def set_object(self, occupant):
        # validate occupant type
        try:
            if occupant != None:
                occupant.get_obj_type() # only objects (artworks and players) have this method
        except AttributeError:
            raise InvalidMove('TypeError placing {}'.format(self, occupant))

        self.occupant = occupant
