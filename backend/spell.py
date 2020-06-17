"""
keeps track of backend of spells, including a pointer to a linked artwork, who owns it, and whether it has been used this turn
""" 
from backend.errors import InvalidMove
from backend.operation import Operation
from backend.user_input import choose_spell

class Spell(object):
    def __init__(self):
        # name, description, color, and artwork are initialized by child constructors
        self.name = None
        self.description = None
        self.color = None
        self.artwork = None
        self.faction = None
        self.tapped = False

    def __str__(self):
        return '{name}\t({faction}:{tapped})'.format(
            name = self.name,
            faction = self.faction or 'No faction',
            tapped = 'Tapped' if self.tapped else 'Untapped',
        )

    def toggle_tapped(self):
        self.tapped = not self.tapped

    def untap(self):
        """Used in Board.end_turn to reset spell states"""
        self.tapped = False

    def cast(self, board, operations):
        # VALIDATE
        #  - current player must own spell
        if self.faction != board.faction:
            raise InvalidMove("{} cannot cast {} because it is owned by {}".format(board.faction, self.name, self.faction))

        # - spell cannot already have been used
        if self.tapped:
            raise InvalidMove("{} already cast".format(self.name))
        
        # - operations must be valid for the spell
        self._validate_operations(board, operations)

        # CAST
        self.toggle_tapped()
        self._apply_operations(board, operations)

    def choose_options(self, board):
        raise NotImplementedError() # must be overwridden
    
    ############################
    # INTERNAL METHODS 
    ############################
    def _validate_operations(self, board, operations):
        raise NotImplementedError() # must be overwridden

    def _apply_operations(self, board, operations):
        [operation.apply(board) for operation in operations]

# TODO: implement _validate_operations for each spell (search for pass in this file)
# there is some decision to be made about how far to go in terms of
#  - only giving the user valid choices
#  - not validating some things and leaving them to be socially enforced
# it seems reasonable to start with asking the needed questions to collect spell
# specific info, giving all options, and applying those options even if illegal
# potential things to validate are marked with TOVALIDATE
class Pristess(Spell):
    def __init__(self, artwork):
        super(Pristess, self).__init__() # initializes faction and tapped
        self.name = 'Pristess'
        self.color = 'Pink'
        self.description = 'Grow linked region'
        self.artwork = artwork

    def _validate_operations(self, board, operations):
        if len(operations) != 1:
            raise InvalidMove('Pristess should make 1 change not {}'.format(len(operations)))

        operation = operations[0]
        if operation.change not in ['l', 'd']:
            raise InvalidMove('Pristess cannot include change {}'.format(operation.change))

        valid_change = board.faction[0].lower() # getting this by slicing the faction name is :(
        if operation.change != valid_change:
            raise InvalidMove('Pristess change must match turn ({} != {})'.format(operation.change, valid_change))

        # TOVALIDATE: check operation.hex is adjacent to pristess artwork linked region

class Purify(Spell):
    def __init__(self):
        super(Purify, self).__init__() # initializes faction and tapped
        self.name = 'Purify'
        self.color = 'Pink'
        self.description = 'Bless underneath adjacent object'

    def _validate_operations(self, board, operations):
        if len(operations) != 1:
            raise InvalidMove('Purify should make 1 change not {}'.format(len(operations)))

        operation = operations[0]
        if operation.change not in ['l', 'd']:
            raise InvalidMove('Purify cannot include change {}'.format(operation.change))

        valid_change = board.faction[0].lower() # getting this by slicing the faction name is :(
        if operation.change != valid_change:
            raise InvalidMove('Purify change must match turn ({} != {})'.format(operation.change, valid_change))

        # TOVALIDATE: check operation.hex is adjacent to player token and has an object on it

class Imposter(Spell):
    def __init__(self, artwork):
        super(Imposter, self).__init__() # initializes faction and tapped
        self.name = 'Imposter'
        self.color = 'Indigo'
        self.description = 'Copy auras from here to linked room'
        self.artwork = artwork

    def _validate_operations(self, board, operations):
        pass

class Imprint(Spell):
    def __init__(self):
        super(Imprint, self).__init__() # initializes faction and tapped
        self.name = 'Imprint'
        self.color = 'Indigo'
        self.description = 'Copy auras from around enemy to self'

    def _validate_operations(self, board, operations):
        pass

class Opportunist(Spell):
    def __init__(self, artwork):
        super(Opportunist, self).__init__()
        self.name = 'Opportunist'
        self.color = 'Orange'
        self.description = 'Ready spell from linked room'
        self.artwork = artwork

    def _validate_operations(self, board, operations):
        if len(operations) != 1:
            raise InvalidMove('Opportunist should make 1 change not {}'.format(len(operations)))
        
        operation = operations[0]
        if operation.change != 'u':
            raise InvalidMove('Opportunist cannot include change {}'.format(operation.change))

        spell_to_untap = operation.extras['spell']
        if isinstance(spell_to_untap, str):
            try:
                spell_to_untap = board.str_to_spell(spell_to_untap)
            except NameError as e:
                raise InvalidMove('{} for Opportunist'.format(e))
        
        if spell_to_untap.faction != board.faction:
            raise InvalidMove('{} cannot use Opportunist on a spell owned by {}'.format(board.faction, spell_to_untap.faction))
        # TOVALIDATE: check operation.extras is a spell owned by the player + is linked

    def cast(self, board, spell_str=None):
        # use spell_str if given, otherwise prompt for input
        if spell_str == None or spell_str == []: # can be [] if called with Spell's params (board, operations)
            print(self.description)
            spell = choose_spell(board)
        else:
            spell = spell_str
        operations = [Operation('n', 'u', {'spell': spell})]
        super(Opportunist, self).cast(board, operations)

class Overwork(Spell):
    def __init__(self):
        super(Overwork, self).__init__() # initializes faction and tapped
        self.name = 'Overwork'
        self.color = 'Orange'
        self.description = 'Gain one action per adjacent object'

    def _validate_operations(self, board, operations):
        for operation in operations:
            if operation.change != 'a':
                raise InvalidMove('Overwork cannot include change {}'.format(operation.change))
        # TOVALIDATE: check operations.length = number of adjacent objects on board

    def cast(self, board):
        # no user input needed
        num_adj_hexes_occupied = 2 # TODO: calculate (or could make user enter it)
        print('Overwork calculation not implemented, assuming 2 adjacent objects')

        operations = [Operation('n', 'a')] * num_adj_hexes_occupied
        super(Overwork, self).cast(board, operations)

class Usurper(Spell):
    def __init__(self, artwork):
        super(Usurper, self).__init__() # initializes faction and tapped
        self.name = 'Usurper'
        self.color = 'Umber'
        self.description = 'Shrink region twice, then grow twice'
        self.artwork = artwork

    def _validate_operations(self, board, operations):
        pass

class Upset(Spell):
    def __init__(self):
        super(Upset, self).__init__() # initializes faction and tapped
        self.name = 'Upset '
        self.color = 'Umber'
        self.description = 'Rearrange auras under & around self'

    def _validate_operations(self, board, operations):
        pass

class Stonemason(Spell):
    def __init__(self, artwork):
        super(Stonemason, self).__init__() # initializes faction and tapped
        self.name = 'Stonemason'
        self.color = 'Sapphire'
        self.description = 'Move linked room anywhere'
        self.artwork = artwork

    def _validate_operations(self, board, operations):
        pass

class Shovel(Spell):
    def __init__(self):
        super(Shovel, self).__init__() # initializes faction and tapped
        self.name = 'Shovel'
        self.color = 'Sapphire'
        self.description = 'Move shovel room to adjacent space'

    def _validate_operations(self, board, operations):
        pass

class Locksmith(Spell):
    def __init__(self, artwork):
        super(Locksmith, self).__init__() # initializes faction and tapped
        self.name = 'Locksmith'
        self.color = 'Lime'
        self.description = 'Move linked object anywhere'
        self.artwork = artwork

    def _validate_operations(self, board, operations):
        pass

class Leap(Spell):
    def __init__(self):
        super(Leap, self).__init__() # initializes faction and tapped
        self.name = 'Leap  '
        self.color = 'Lime'
        self.description = 'Trade places with object in row'

    def _validate_operations(self, board, operations):
        pass

class Yeoman(Spell):
    def __init__(self, artwork):
        super(Yeoman, self).__init__() # initializes faction and tapped
        self.name = 'Yeoman'
        self.color = 'Yellow'
        self.description = 'Rearrange objects in linked rooms'
        self.artwork = artwork

    def _validate_operations(self, board, operations):
        pass

class Yoke(Spell):
    def __init__(self):
        super(Yoke, self).__init__() # initializes faction and tapped
        self.name = 'Yoke  '
        self.color = 'Yellow'
        self.description = 'Move self and object one space'

    def _validate_operations(self, board, operations):
        pass

if __name__ == "__main__":
    # run this code from /piously with `python3 -m backend.spell`
    from backend.board import Board

    # get board and two spell
    b = Board("Light")
    opportunist = b.str_to_spell('q')
    to_untap = b.str_to_spell('w')
    print(opportunist)
    print(to_untap)
    
    # init values
    opportunist.faction = "Light"
    to_untap.faction = "Light"
    to_untap.toggle_tapped() 
    print(opportunist)
    print(to_untap)
    
    # casting opportunist should untap the indicated spell and tap opportunist
    opportunist.cast(b, 'w')
    print(opportunist)
    print(to_untap)
