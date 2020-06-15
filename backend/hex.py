"""
hex represents one of 28 hexes on the Piously board. 
"""

class Hex(object):
    def __init__(self, _location):
        self.location = _location
        self.aura = None
        self.occupant = None

    def __str__(self):
        return 'Hex{{({location}), aura:{aura}, occupant:{occupant}}}'.format(
            location = self.location,
            aura = self.aura,
            occupant = self.occupant,
        )

    def toggle_aura(self):
        if self.aura == None:
            self.aura = "Dark"
        elif self.aura == "Dark":
            self.aura = "Light"
        elif self.aura == "Light":
            self.aura = None
        else:
            raise NameError('Hex cannot have aura value "{}".'.format(self.aura))

if __name__ == "__main__":
    h = Hex(2)
    # h.aura = 'bad'
    h.toggle_aura()
    print(h)
