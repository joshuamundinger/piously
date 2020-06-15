"""
One of the two player pieces on the board
"""


class Player(object):

    def __init__(self, faction):
        self.faction = faction
        self.hex = None

    def __str__(self):
        return '{faction}\t({location})'.format(
            faction = self.faction,
            location = self.hex and self.hex.location or 'Not placed'
        )