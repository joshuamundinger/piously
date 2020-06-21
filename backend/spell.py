"""
keeps track of backend of spells, including a pointer to a linked artwork,
who owns it, and whether it has been used this turn
"""
from backend.room import Room
from backend.errors import InvalidMove
from backend.location import find_adjacent_hexes
from backend.operation import Operation
from graphics.screen_input import choose_from_list
import graphics.screen_input as screen_input
from copy import deepcopy
import backend.location as location
import numpy as np

"""
method to place auras on hexes, used in Imposter and Upset
place_auras_on_hexes replaces the auras on the hexes in hex_list with
those in aura_list, based on user input

Params:
 - aura_list: list of auras to place (entries should be 'Dark' or 'Light'). None entries
    will automatically be removed
 - hex_list: list of hexes to put auras on
"""
def place_auras_on_hexes(board, aura_list, hex_list):
    # clean the list of empty auras
    aura_list = [aura for aura in aura_list if aura]
    if len(aura_list) > len(hex_list):
        raise RuntimeError('Pidgeonhole Problem: tried to put too many auras on a set of hexes')
    remaining_auras = deepcopy(aura_list)
    # clear auras in target room
    for hex in hex_list:
        hex.aura = None
    board.flush_aura_data()
    for aura in aura_list:
        remaining_auras.remove(aura)
        new_hex = screen_input.choose_hexes(
            board.screen,
            [hex for hex in hex_list if not hex.aura],
            prompt_text = "Choose a hex for aura {}\n Auras remaining: {}".format(aura, remaining_auras),
        )
        new_hex.aura = aura
        board.flush_aura_data()


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
        return self.name

    def untap(self):
        """Used in Board.end_turn to reset spell states"""
        self.tapped = False

    def cast(self, board, *args):
        raise NotImplementedError() # must be overwridden

    ############################
    # INTERNAL METHODS
    ############################
    def _validate_spell_status(self, board):
        # current player must own spell
        if self.faction != board.faction:
            raise InvalidMove("{} cannot cast {} because it is owned by {}".format(
                board.faction,
                self.name,
                self.faction,
            ))

        # spell cannot already have been used
        if self.tapped:
            raise InvalidMove("{} already cast".format(self.name))

        # artwork must also have correct status
        self._validate_artwork_status(board)

    def _validate_artwork_status(self, board):
        # if the spell has an artwork, check if it's placed on the board, on your aura
        if self.artwork:
            if self.artwork.hex:
                if self.artwork.hex.aura != board.faction:
                    raise InvalidMove('{} is not on player\'s aura'.format(self.name))
            else:
                raise InvalidMove('{} is not placed on board'.format(self.name))

    def _shared_cast(self, board, operations=[]):
        self._validate_operations(board, operations)
        self._toggle_tapped()
        self._apply_operations(board, operations)

    def _validate_operations(self, board, operations):
        raise NotImplementedError() # must be overwridden

    def _toggle_tapped(self):
        self.tapped = not self.tapped

    def _apply_operations(self, board, operations):
        [operation.apply(board) for operation in operations]

# TODO: implement _validate_operations for each spell (search for pass in this file)
# there is some decision to be made about how far to go in terms of
#  - only giving the user valid choices
#  - not validating some things and leaving them to be socially enforced
# it seems reasonable to start with asking the needed questions to collect spell
# specific info, giving all options, and applying those options even if illegal
# potential things to validate are marked with TOVALIDATE

# TODO: implement click-based input for all spells.
# Completed so far: P spells
class Priestess(Spell):
    def __init__(self, artwork):
        super(Priestess, self).__init__() # initializes faction and tapped
        self.name = 'Priestess'
        self.color = 'Pink'
        self.description = 'Grow linked region'
        self.artwork = artwork

    def cast(self, board):
        self._validate_spell_status(board)

        # choose the hex to bless
        adjacent_linked_hexes = location.adjacent_linked_region(board, board.artworks[0].hex)
        target_hex = screen_input.choose_hexes(
            board.screen,
            adjacent_linked_hexes,
            prompt_text = self.description
        )
        if not target_hex:
            raise InvalidMove('There are no hexes which the Priestess may bless')
        print('Using the Priestess on {}'.format(target_hex))
        target_hex.aura = board.faction
        self._toggle_tapped()

class Purify(Spell):
    def __init__(self):
        super(Purify, self).__init__() # initializes faction and tapped
        self.name = 'Purify'
        self.color = 'Pink'
        self.description = 'Bless underneath adjacent object'

    def cast(self, board):
        self._validate_spell_status(board)
        adj_hexes = find_adjacent_hexes(board, board.get_current_player().hex)
        # get list of occupied neighbors which are the wrong aura
        purifiable_hexes = [h for h in adj_hexes if (h.occupant and h.aura != board.faction)]
        # choose from neighbors which are occupied
        hex = screen_input.choose_hexes(
            board.screen,
            purifiable_hexes,
            prompt_text = self.description,
        )
        if not hex:
            raise InvalidMove('No hexes to Purify')
        print('Using Purify on {}'.format(hex))
        hex.aura = board.faction
        self._toggle_tapped()

class Imposter(Spell):
    def __init__(self, artwork):
        super(Imposter, self).__init__() # initializes faction and tapped
        self.name = 'Imposter'
        self.color = 'Indigo'
        self.description = 'Copy auras from Imposter\'s room to linked room'
        self.artwork = artwork

    def _validate_operations(self, board, operations):
        pass

    def cast(self, board):
        self._validate_spell_status(board)
        print(self.description)
        # get a linked room.
        target_room = choose_from_list(
            board.screen,
            location.linked_rooms(board, self.artwork.hex),
            prompt_text = 'Choose room to copy to:',
        )
        # get list of auras in artwork's room
        aura_list = [hex.aura for hex in self.artwork.hex.room.hexes if hex.aura]
        # TODO: handle if you are copying more than one aura onto the Shovel
        place_auras_on_hexes(board, aura_list, target_room.hexes)
        self._shared_cast(board)

class Imprint(Spell):
    def __init__(self):
        super(Imprint, self).__init__() # initializes faction and tapped
        self.name = 'Imprint'
        self.color = 'Indigo'
        self.description = 'Copy auras from around enemy to self'

    def _validate_operations(self, board, operations):
        pass

    def cast(self, board):
        self._validate_spell_status(board)

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
        current_player_neighborhood = location.find_adjacent_hexes(
            board,
            current_player.hex,
            return_nones = True,
        )
        for i in range(6):
            if opposing_neighboring_auras[i] != 'Skip' and current_player_neighborhood[i]:
                current_player_neighborhood[i].aura = opposing_neighboring_auras[i]
        self._shared_cast(board)

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
            raise InvalidMove('{} cannot use Opportunist on a spell owned by {}'.format(
                board.faction,
                spell_to_untap.faction,
        ))
        # TOVALIDATE: check operation.extras is a spell owned by the player + is linked

    def cast(self, board, spell_str=None):
        self._validate_spell_status(board)

        # TODO: remove all use of spell_str and Operation
        if spell_str != None:
            raise NotImplementedError('Opportunist doesnt support spell_str')

        eligible_spells = []
        for spell in board.spells:
            if spell.faction == board.faction and spell.tapped:
                # TODO: add verification for chosen spell's room to be linked to the Opportunist
                eligible_spells.append(spell)
        spell = choose_from_list(board.screen, eligible_spells)
        if not spell:
            raise InvalidMove('There are no linked untapped spells')

        operations = [Operation('n', 'u', {'spell': spell})]
        self._shared_cast(board, operations)

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
        self._validate_spell_status(board)

        # no user input needed
        adj_hexes = location.find_adjacent_hexes(board, board.get_current_player().hex)
        num_adj_hexes_occupied = len([ x for x in adj_hexes if x.occupant])
        operations = [Operation('n', 'a')] * num_adj_hexes_occupied
        self._shared_cast(board, operations)

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
        self._validate_spell_status(board)
        self._toggle_tapped()
        # pick two linked hexes to flip
        for i in range(2):
            hex_to_flip = screen_input.choose_hexes(
                board.screen,
                location.linked_hexes(board, self.artwork.hex),
                prompt_text = 'Pick a hex on which to flip',
            )
            hex_to_flip.toggle_aura()
            board.flush_aura_data()
            # check to see if we flipped under the artwork/
            # if so, stop Usurping
            if self.artwork.hex.aura != board.faction:
                return None
        for i in range(2):
            hex_to_change = screen_input.choose_hexes(
                board.screen,
                location.adjacent_linked_region(board, self.artwork.hex),
                prompt_text = 'Pick a hex on which to grow',
            )
            hex_to_change.aura = board.faction
            board.flush_aura_data()

class Upset(Spell):
    def __init__(self):
        super(Upset, self).__init__() # initializes faction and tapped
        self.name = 'Upset '
        self.color = 'Umber'
        self.description = 'Rearrange auras under & around self'

    def _validate_operations(self, board, operations):
        pass

    def cast(self, board):
        self._validate_spell_status(board)
        # get neighborhood of 7 hexes and their auras
        neighborhood = location.find_adjacent_hexes(board, board.get_current_player().hex)
        neighborhood.append(board.get_current_player().hex)
        # get auras on neighborhood
        aura_list = [x.aura for x in neighborhood if x.aura]
        # rearrange auras in neighborhood
        place_auras_on_hexes(board, aura_list, neighborhood)
        self._toggle_tapped()

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
        self.description = "Move Shovel room to adjacent space,\n or if you\'re on it, move Shovel room anywhere"

    def _validate_operations(self, board, operations):
        pass

    def create_Shovel_room(self, location):
        return Room("v",
            location, [],
            None, None
            )

    def cast(self, board):
        # check if the shovel has been placed yet
        if len(board.rooms) == 7:
            # time to place the shovel!
            # make temporary room with hexes adjacent to current player
            player_hex = board.get_current_player().hex
            new_hex_locations = location.find_unoccupied_neighbors(board,[player_hex])
            # make room with hexes at new_hex_locations, and choose from them
            if not new_hex_locations:
                raise InvalidMove("There's nowhere to place the Shovel")
            root = new_hex_locations.pop(0)
            board.rooms.append(Room("t",
                root,
                new_hex_locations,None,None,relative_shape=False)
            )
            board.flush_hex_data()
            shovel_location = screen_input.choose_hexes(board.screen, 
                board.rooms[7].hexes,
                prompt_text = "Choose where the Shovel will go").location
            board.rooms.pop()
            board.rooms.append(self.create_Shovel_room(shovel_location))       
            board.flush_hex_data()
        else:
            # time to move the shovel!
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

    def cast(self, board):
        self._validate_spell_status(board)
        # get list of linked objects
        linked_hexes = location.linked_hexes(board, self.artwork.hex)
        linked_objects = [hex.occupant for hex in linked_hexes if hex.occupant]

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
        target_object = choose_from_list(
            board.screen,
            linked_objects,
            prompt_text='Choose object to move',
        )
        target_hex = screen_input.choose_hexes(
            board.screen,
            target_hexes,
            prompt_text='Choose where to move {}'.format(target_object)
        )
        board.move_object(target_object, from_hex = target_object.hex, to_hex = target_hex)
        self._toggle_tapped()

class Leap(Spell):
    def __init__(self):
        super(Leap, self).__init__() # initializes faction and tapped
        self.name = 'Leap  '
        self.color = 'Lime'
        self.description = 'Trade places with object in row'

    def _validate_operations(self, board, operations):
        pass

    def cast(self, board, hex_str=None):
        self._validate_spell_status(board)
        if not hex_str:
            current_player = board.get_current_player()

            # get list of leap-able objects
            leapable_objects = []
            for obj in board.get_placed_non_player_objects():
                if location.leap_eligible(board, current_player.hex, obj.hex):
                    leapable_objects.append(obj)

            target_object = choose_from_list(
                board.screen,
                leapable_objects,
                'Pick an object to Leap with',
            )
            if not target_object:
                raise InvalidMove('There\'s no object to Leap with')
        board.swap_object(current_player, target_object)
        # TODO: test
        self._toggle_tapped()

class Yeoman(Spell):
    def __init__(self, artwork):
        super(Yeoman, self).__init__() # initializes faction and tapped
        self.name = 'Yeoman'
        self.color = 'Yellow'
        self.description = 'Rearrange objects in linked rooms'
        self.artwork = artwork

    def _validate_operations(self, board, operations):
        pass

    # TODO: redo so that partial placements may be flushed to the board
    def cast(self,board,str=[]):
        self._validate_artwork_status(board)
        # get linked rooms
        populated_linked_rooms = location.linked_rooms(board, self.artwork.hex)
        # for each room, find the objects in the room.
        # If there are no objects, remove the room from the list,
        # so that only populated rooms remain
        for room in populated_linked_rooms:
            occupants = [hex.occupant for hex in room.hexes]
            # only keep track of objects in rooms which have at least one object and more than one hex
            if not (any(occupants) and len(room.hexes) > 1):
                populated_linked_rooms.remove(room)
        # loop through all rooms, and rearrange the objects in each room
        for room in populated_linked_rooms:
            # move objects that used to be in the room, one at a time.
            unoccupied_locations = [hex.location for hex in room.hexes]
            object_location_pairs = []
            for hex in room.hexes:
                # assign a new location to the object on this hex, if there is one
                # this assignment goes into object_location_pairs
                if hex.occupant:
                    # choose a hex not yet targeted
                    target_hex_index = screen_input.choose_hexes(
                        board.screen,
                        [location.find_hex(board,loc) for loc in unoccupied_locations],
                        prompt_text="Pick a hex for {}".format(hex.occupant),
                        return_index = True
                    )
                    # keep track of the new location for the object
                    object_location_pairs.append((hex.occupant, unoccupied_locations[target_hex_index]))
                    hex.occupant = None
                    unoccupied_locations.pop(target_hex_index)
            # update the board with new locations
            for object_to_place, loc in object_location_pairs:
                target_hex = location.find_hex(board, loc)
                target_hex.occupant = object_to_place
                object_to_place.hex = target_hex
        self._toggle_tapped()


class Yoke(Spell):
    def __init__(self):
        super(Yoke, self).__init__() # initializes faction and tapped
        self.name = 'Yoke  '
        self.color = 'Yellow'
        self.description = 'Move self and object one space'

    def _validate_operations(self, board, operations):
        pass

    def cast(self, board, hex_str=None):
        self._validate_spell_status(board)
        current_player = board.get_current_player()
        if not hex_str:
            # get target object for yoking
            target_object = choose_from_list(
                board.screen,
                board.get_placed_non_player_objects(),
                'Pick an object to Yoke with',
            )
            if not target_object:
                # you shouldn't be here: there should always be at least two objects
                raise InvalidMove('There was no other object to Yoke')
            # get directions for yolking
            # elements are: (player_destination, target_destination)
            possible_location_data = []
            for u in location.unit_directions:
                player_destination = location.find_neighbor_hex(board, current_player.hex, u)
                target_destination = location.find_neighbor_hex(board, target_object.hex, u)
                player_can_move = player_destination and (
                    not(player_destination.occupant) or player_destination.occupant == target_object
                )
                target_can_move = target_destination and (
                    not(target_destination.occupant) or target_destination.occupant == current_player
                )
                if (player_can_move and target_can_move):
                    possible_location_data.append((player_destination, target_destination))
            # if there's more than one direction, ask user for input
            player_direction = screen_input.choose_hexes(
                board.screen,
                [x[0] for x in possible_location_data],
                prompt_text="Choose the destination of the player"
            )
            if player_direction == None:
                raise InvalidMove('These two objects have no common direction to move')
            # get the directions of both player and target by finding the entry
            # whose first entry is the player
            movement_data = [x for x in possible_location_data if x[0] == player_direction][0]
            # move the player and object
            current_player.hex.occupant = None
            target_object.hex.occupant = None
            current_player.hex = movement_data[0]
            target_object.hex = movement_data[1]
            current_player.hex.occupant = current_player
            target_object.hex.occupant = target_object
            self._toggle_tapped()
