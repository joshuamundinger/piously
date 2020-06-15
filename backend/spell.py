"""
keeps track of backend of spells, including a pointer to a linked artwork, who owns it, and whether it has been used this turn
""" 
from errors import InvalidMove

class Spell(object):
    def __init__(self, name, description, color, artwork=None):
        self.name = name
        self.description = description
        self.color = color
        self.artwork = artwork
        self.faction = None
        self.tapped = False

    def __str__(self):
        return '{name}\t({faction}:{tapped})'.format(
            name = self.name,
            faction = self.faction or 'No faction',
            tapped = 'Tapped' if self.tapped else 'Untapped',
        )

    def cast(self):
        if not self.tapped:
            self.toggle_tapped()
        else:
            raise InvalidMove("{} already cast".format(self.name))

    def toggle_tapped(self):
        self.tapped = not self.tapped

    def untap(self):
        """Used in Board.end_turn to reset spell states"""
        self.tapped = False

if __name__ == "__main__":
    s = Spell('Overwork', '+1 Action for each adj. object', 'O')
    print(s.tapped)
    s.cast()
    print(s.tapped)
    try:
        s.cast()
    except InvalidMove as e:
        print(e)
