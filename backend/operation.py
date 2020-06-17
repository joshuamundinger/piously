"""
A single operation on the board. 
 - all params in the constructor are strings to allow creating operations based on keyboard input
 - each operation knows how to apply the relevant change to the board

Params:
 - hex: a Hex object OR a string (sorry), if it is a string it should be one of [1234 5678 qwer tyui asdf ghjk zxcv b n]
    - b  = shovel
    - n  = none
 - change: string, one of: (* means requires extra info)
    - l  = change to light aura
    - d  = change to dark aura
    - n  = change to no aura
    - a  = add action
    - s  = subtract action
    - m* = move to location
    - p* = place object
    - r* = remove object
    - u* = untap a spell
    - TODO: maybe add c* = claim spell and replace logic in Game.maybe_claim_spell()
 - extras: dict string -> string, keys are one of [occupant location spell]
    - occupant: value can be one of [1 5 q t a g z d l]
        - d = dark player
        - l = light player
    - locations: [x, y]
    - spells: value can be a Spell or a string, one of [12 56 qw ty as gh zx] (first one is artwork, second is bewitchment)
"""

class Operation(object):
    def __init__(self, hex, change, extras={}):
        # note: hex can be a string or a Hex object
        self.hex = hex
        self.change = change
        self.extras = extras

    def apply(self, board):
        # TODO: remove try-except here once hexes are initialized on board
        if isinstance(self.hex, str):
            try:
                hex = board.str_to_hex(self.hex)
            except IndexError:
                print('hex {} not found'.format(self.hex))
        else:
            hex = self.hex

        if self.change == 'l' or self.change == 'Light': # change to light aura
            hex.aura = "Light"
        elif self.change == 'd' or self.change == 'Dark': # change to dark aura
            hex.aura = "Dark"
        elif self.change == 'n': # change to no aura
            hex.aura = None
        elif self.change == 'a': # add action
            board.actions += 1
        elif self.change == 's': # subtract action
            board.actions -= 1
        elif self.change == 'm': # move hex to location
            hex.location = self.extras['location']
        elif self.change == 'p': # place object
            occupant = board.str_to_occupant(self.extras['occupant'])
            occupant.hex = hex
            hex.occupant = occupant
        elif self.change == 'r': # remove object
            occupant = board.str_to_occupant(self.extras['occupant'])
            occupant.hex = None
            hex.occupant = None
        elif self.change == 'u': # untap a spell
            spell = self.extras['spell']
            if isinstance(spell, str):
                spell = board.str_to_spell(spell)
            spell.untap()
        elif self.change == 'c': # claim a spell
            spell = self.extras['spell']
            if isinstance(spell, str):
                spell = board.str_to_spell(spell)
            spell.faction = board.faction
        else:
            raise RuntimeError('Invalid change {}'.format(self.change))
