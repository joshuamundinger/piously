"""
hex represents one of 28 hexes on the Piously board. 
"""

class Hex(object):
    def __init__(self, _location):
        self.location = _location
        self.aura = None
        self.occupant = None

    def toggle_aura():
        if self.aura == None
            self.aura = "Dark"
        else if self.aura == "Dark"
            self.aura = "Light"
        else if self.aura == "Light"
            self.aura = None
        else:
            raise RuntimeError "An aura was mis-set."
    
    


