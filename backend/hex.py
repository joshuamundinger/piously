"""
hex represents one of 28 hexes on the Piously board.
"""
from backend.helpers import other_faction

class Hex(object):
    def __init__(self, room, location):
        self.room = room
        self.location = location
        self.aura = None
        self.occupant = None

    def __str__(self):
        return 'Hex{{({location}), aura:{aura}, occupant:{occupant}}}'.format(
            location = self.location,
            aura = self.aura,
            occupant = self.occupant,
        )

    # TODO: maybe remove
    def toggle_aura(self):
        self.aura = other_faction(self.aura)
        
if __name__ == "__main__":
    h = Hex('Yellow', 2) # these are not the right formats for these params
    # h.aura = 'bad'
    h.toggle_aura()
    print(h)
