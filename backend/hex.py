"""
hex represents one of 28 hexes on the Piously board. 
"""

class Hex(object):
    def __init__(self, _location):
        self.location = _location
        self.aura = None
        self.occupant = None

    def toggle_aura(self):
        if self.aura == None:
            self.aura = "Dark"
        elif self.aura == "Dark":
            self.aura = "Light"
        elif self.aura == "Light":
            self.aura = None
        else:
            raise RuntimeError("An aura was mis-set.")
    
    


