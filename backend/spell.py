"""
keeps track of backend of spells, including a pointer to a linked artwork, who owns it, and whether it has been used this turn
""" 

class Spell(object):
    def __init__(self, name, description, color, artwork=None):
        self.name = name
        self.description = description
        self.color = color
        self.artwork = artwork
        self.faction = None
        self.tapped = False

    def cast(self):
        if not self.tapped:
            self.toggle_tapped()
        else:
            raise RuntimeError("Invalid move: spell already cast")

    def toggle_tapped(self):
        self.tapped = not self.tapped

if __name__ == "__main__":
    s = Spell('Overwork', '+1 Action for each adj. object', 'O')
    print(s.tapped)
    s.cast()
    print(s.tapped)
    try:
        s.cast()
    except RuntimeError as e:
        print(e)