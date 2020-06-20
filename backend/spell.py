"""
keeps track of backend of spells, including a pointer to a linked artwork, who owns it, and whether it has been used this turn
""" 
from backend.errors import InvalidMove
from backend.location import find_adjacent_hexes
from backend.operation import Operation
from backend.user_input import choose_spell, choose_from_list
from copy import deepcopy
import backend.location as location

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

    def _validate_artwork_position(self, board):
        # if the spell has an artwork, check if it's placed on the board, on your aura
        if self.artwork:
            if self.artwork.hex:
                if self.artwork.hex.aura != board.faction:
                    raise InvalidMove('{} is not on player\'s aura'.format(self.name))
            else: 
                raise InvalidMove('{} is not placed on board'.format(self.name))


# TODO: implement _validate_operations for each spell (search for pass in this file)
# there is some decision to be made about how far to go in terms of
#  - only giving the user valid choices
#  - not validating some things and leaving them to be socially enforced
# it seems reasonable to start with asking the needed questions to collect spell
# specific info, giving all options, and applying those options even if illegal
# potential things to validate are marked with TOVALIDATE
class Priestess(Spell):
    def __init__(self, artwork):
        super(Priestess, self).__init__() # initializes faction and tapped
        self.name = 'Priestess'
        self.color = 'Pink'
        self.description = 'Grow linked region'
        self.artwork = artwork

    def _validate_operations(self, board, operations):
        if len(operations) != 1:
            raise InvalidMove('Priestess should make 1 change not {}'.format(len(operations)))

        operation = operations[0]
        valid_changes = [board.faction, board.faction[0].lower()] # getting this by slicing the faction name is :(
        if operation.change not in valid_changes:
            raise InvalidMove('Priestess change cannot be {}'.format(operation.change))

        # TOVALIDATE: check operation.hex is adjacent to pristess artwork linked region

    def cast(self,board,hex_str=None):
        self._validate_artwork_position(board)
        # prompt if no hex was passed
        if hex_str == None or hex_str == []:
            print(self.description)
            target_hex = choose_from_list(location.adjacent_linked_region(board, board.artworks[0].hex))
            if not target_hex:
                raise InvalidMove('There are no hexes which the Priestess may bless')
            print('Using the Priestess on {}'.format(target_hex))

            
        else:
            target_hex = hex_str

        operations = [Operation(target_hex, board.faction)]
        super(Priestess, self).cast(board, operations)

        """
        # alternative version 
        target_hex.aura = board.faction
        """ 


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
        valid_changes = [board.faction, board.faction[0].lower()] # getting this by slicing the faction name is :(
        if operation.change not in valid_changes:
            raise InvalidMove('Purify change cannot be {}'.format(operation.change))

        # TOVALIDATE: check operation.hex is adjacent to player token and has an object on it

    def cast(self, board, hex_str=None):
        # use hex_str if given, otherwise prompt for input
        if hex_str == None or hex_str == []: # can be [] if called with Spell's params (board, operations)
            print(self.description)
            adj_hexes = find_adjacent_hexes(board, board.get_current_player().hex)
            # choose from neighbors which are occupied
            hex = choose_from_list([h for h in adj_hexes if h.occupant != None])
            if not hex:
                raise InvalidMove('No adjacent hexes have an object')
            print('Using Purify on {}'.format(hex))
        else:
            hex = hex_str

        # TOVALIDATE: hex is not already occupied by that color aura
        operations = [Operation(hex, board.faction)]
        super(Purify, self).cast(board, operations)

class Imposter(Spell):
    def __init__(self, artwork):
        super(Imposter, self).__init__() # initializes faction and tapped
        self.name = 'Imposter'
        self.color = 'Indigo'
        self.description = 'Copy auras from here to linked room'
        self.artwork = artwork

    def _validate_operations(self, board, operations):
        pass

    def cast(self,board):
        self._validate_artwork_position(board)
        # get a linked room.
        target_room = choose_from_list(location.linked_rooms(board, self.artwork.hex))
        # get list of auras in artwork's room
        aura_list = deepcopy([hex.aura for hex in self.artwork.hex.room.hexes])
        for hex in target_room.auras:
            new_aura = choose_from_list(aura_list, prompt_text="Aura for hex at {}".format(hex.location))
            hex.aura = new_aura
            aura_list.remove(new_aura)

            # TODO: test

class Imprint(Spell):
    def __init__(self):
        super(Imprint, self).__init__() # initializes faction and tapped
        self.name = 'Imprint'
        self.color = 'Indigo'
        self.description = 'Copy auras from around enemy to self'

    def _validate_operations(self, board, operations):
        pass

    def cast(self, board):
        # requires no input from player
        # get auras around opponent
        current_player = board.get_current_player() 
        opposing_player = board.get_opposing_player()
        opposing_neighboring_auras = []
        for hex in location.find_adjacent_hexes(board,opposing_player.hex, return_nones=True):
            if hex:
                opposing_neighboring_auras.append(hex.aura)
            else:
                opposing_neighboring_auras.append('Skip')
        # now put auras on neighborhood of current_player
        current_player.hex.aura = opposing_player.hex.aura
        current_player_neighborhood = location.find_adjacent_hexes(board,current_player.hex,return_nones=True)
        for i in range(6):
            if opposing_neighboring_auras[i] != 'Skip':
                current_player_neighborhood[i].aura = opposing_neighboring_auras[i]
        
        # TODO: test

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
        # TODO: add verification for chosen spell's room to be linked to the Opportunist
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
        adj_hexes = location.find_adjacent_hexes(board, board.get_current_player().hex)
        num_adj_hexes_occupied = len([ x for x in adj_hexes if x.occupant])
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

    def cast(self, board):
        self._validate_artwork_position(board)
        test_board = deepcopy(board)
        # pick two linked hexes to flip
        for i in range(2):
            hex_to_flip = choose_from_list(location.linked_hexes(test_board, self.artwork.hex), 
                prompt_text='Pick a hex on which to flip')
            hex_to_flip.toggle_aura()
            #check to see if we flipped under the artwork
            self._validate_artwork_position(test_board)
        for i in range(2):
            hex_to_change = choose_from_list(location.adjacent_linked_region(test_board, self.artwork.hex),
                prompt_text='Pick a hex on which to grow')
            hex_to_change.aura = test_board.get_current_player()
        board = test_board
        # TODO: test

class Upset(Spell):
    def __init__(self):
        super(Upset, self).__init__() # initializes faction and tapped
        self.name = 'Upset '
        self.color = 'Umber'
        self.description = 'Rearrange auras under & around self'

    def _validate_operations(self, board, operations):
        pass

    def cast(self, board):
        # get hexes and their auras
        neighborhood = [board.get_current_player().hex] + location.find_adjacent_hexes(board, board.get_current_player().hex)
        n_auras = deepcopy([x.aura for x in neighborhood])
        for hex in neighborhood:
            new_aura = choose_from_list(n_auras, prompt_text="Pick aura for hex {}".format(hex))
            hex.aura = new_aura
            n_auras.remove(new_aura)
            # TODO: test

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

    def cast(self, board, hex_str = None):
        self._validate_artwork_position(board)
        # get list of linked objects
        linked_objects = [hex.occupant for hex in location.linked_hexes(board,self.artwork.hex) if hex.occupant != None]
        # get list of hexes to move to from the board
        target_hexes = []
        for room in board.rooms:
            for hex in room.hexes:
                if hex.occupant == None:
                    target_hexes.append(hex)
        if target_hexes == []:
            raise InvalidMove('All hexes are occupied.')
        # choose a linked object to move. There should always be at least one, 
        # since we've validated that the Locksmith is on an aura
        target_object = choose_from_list(linked_objects)
        target_hex = choose_from_list(target_hexes)
        board.move_object(target_object, from_hex = target_object.hex, to_hex = target_hex)

        # TODO: test

class Leap(Spell):
    def __init__(self):
        super(Leap, self).__init__() # initializes faction and tapped
        self.name = 'Leap  '
        self.color = 'Lime'
        self.description = 'Trade places with object in row'

    def _validate_operations(self, board, operations):
        pass

    def cast(self, board, hex_str=None):
        if not hex_str:
            current_player = board.get_current_player()
            # get list of leap-able objects
            leapable_objects = [obj for obj in board.get_placed_non_player_objects() if location.leap_eligible(board, current_player.hex, obj.hex)]
            target_object = choose_from_list(leapable_objects, 'Pick an object to Leap with')
            if not target_object:
                raise InvalidMove('There\'s no object to Leap with')
        board.swap_object(current_player, target_object)        
        # TODO: test

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

    def cast(self, board, hex_str = None):
        if not hex_str:
            # get target object for yoking
            target_object = choose_from_list(board.get_placed_non_player_objects(), 'Pick an object to Yoke with')
            if not target_object:
                # you shouldn't be here: there should always be at least two objects
                raise InvalidMove('There was no other object to Yoke')
            # get directions for yolking
            possible_directions = []
            for u in location.unit_directions:
                player_destination = location.find_neighbor_hex(board, board.get_current_player().hex, u)
                target_destination = location.find_neighbor_hex(board, target_object.hex, u)
                # TODO: implement that one of the pieces may move onto the space currently occupied by the other.
                player_can_move = player_destination and not(player_destination.occupant)
                target_can_move = target_destination and not(target_destination.occupant)
                if (player_can_move and target_can_move):
                    possible_directions.append(u)
            # if there's more than one direction, ask user for input
            target_direction = choose_from_list(possible_directions)
            if (target_direction == None).any():
                raise InvalidMove('These two objects have no common direction to move')

        # TODO: implement movement
        raise InvalidMove('Casting not implemented')

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
