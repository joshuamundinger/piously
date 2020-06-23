"""
One of the seven magical artworks. Like Players, Artworks can occupy a Hex.
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

        return "{color} artwork".format(color = self.color)
