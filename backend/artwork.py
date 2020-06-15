"""
One of the seven magical artworks.
"""

class Artwork(object):
    def __init__(self, color):
        self.color = color
        self.hex = None
        self.faction = None

    def __str__(self):
        return "{color}\t({faction}:{location})".format(
            color = self.color,
            faction = self.faction or 'No faction',
            location = self.hex and self.hex.location or 'Not placed'
        )
