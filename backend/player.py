"""
One of the two player pieces on the board
"""

class Player(object):
    def __init__(self, faction):
        self.faction = faction
        self.hex = None

    def __str__(self):
        return '{faction} player'.format(
            faction = self.faction,
        )

    def get_color(self):
        return self.faction

    def get_type(self):
        return 'player'
