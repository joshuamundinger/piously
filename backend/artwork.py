"""
One of the seven magical artworks.
"""

class Artwork(object):
    def __init__(self, color):
        self.color = color
        self.hex = None
        self.faction = None

    def __str__(self):
        location = 'Not placed'
        if self.hex != None:
            location = self.hex.location
        
        return "{color}\t({faction}:{location})".format(
            color = self.color,
            faction = self.faction or 'No faction',
            location = location,
        )
