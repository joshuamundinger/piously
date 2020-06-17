"""
One of the two player pieces on the board
"""

class Player(object):
    def __init__(self, faction):
        self.faction = faction
        self.hex = None

    def __str__(self):
        if self.hex == None:
            location = 'Not placed'
        else:
            location = self.hex.location
        return '{faction}\t({location})'.format(
            faction = self.faction, 
            location = location,
        )

