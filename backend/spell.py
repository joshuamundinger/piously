"""
This file defines the Spell class and 14 Spell subclasses each of
which implement cast(), which is the main method that encodes Spell behavior.

Each Spell includes a name, description, who owns it, whether it has been used this turn,
and may have a pointer to an associated artwork.
"""
from backend.errors import InvalidMove
from backend.helpers import other_faction
from backend.room import Room
from graphics.screen_input import choose_from_list, choose_hexes, get_keypress
from copy import deepcopy

import backend.location as location
import numpy as np

class Spell(object):
    def __init__(self):
        # name, description, color, and artwork are filled in by child constructors
        self.name = None
        self.description = None
        self.color = None
        self.artwork = None

        # faction and tapped are initialized here
        self.faction = None
        self.tapped = False # has the spell been used this turn

    def __str__(self):
        return self.name

    def cast(self, board):
        raise NotImplementedError() # must be overwridden

    def untap(self):
        """Used in Board.end_turn to reset spell states"""
        self.tapped = False

    ############################
    # INTERNAL METHODS
    ############################

    # This should be called at the start of all cast() methods
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

    # TODO: verify all spells call this and _validate_spell_status in their cast method
    # This should be called at the end of all cast() methods
    def _toggle_tapped(self):
        self.tapped = not self.tapped

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
        target_hex = choose_hexes(
            board.screen,
            adjacent_linked_hexes,
            prompt_text = 'Click hex to grow linked region'
        )
        if not target_hex:
            raise InvalidMove('There are no hexes which the Priestess may bless')

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
        adj_hexes = location.find_adjacent_hexes(board, board.get_current_player().hex)
        # get list of occupied neighbors which are the wrong aura
        purifiable_hexes = [h for h in adj_hexes if (h.occupant and h.aura != board.faction)]
        # choose from neighbors which are occupied
        hex = choose_hexes(
            board.screen,
            purifiable_hexes,
            prompt_text = 'Click hex to bless',
        )
        if not hex:
            raise InvalidMove('No hexes to Purify')

        hex.aura = board.faction
        self._toggle_tapped()

class Imposter(Spell):
    def __init__(self, artwork):
        super(Imposter, self).__init__() # initializes faction and tapped
        self.name = 'Imposter'
        self.color = 'Indigo'
        self.description = 'Copy auras from Imposter\'s room to linked room'
        self.artwork = artwork

    def cast(self, board):
        self._validate_spell_status(board)
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
        self._toggle_tapped()

class Imprint(Spell):
    def __init__(self):
        super(Imprint, self).__init__() # initializes faction and tapped
        self.name = 'Imprint'
        self.color = 'Indigo'
        self.description = 'Copy auras from around enemy to self'

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
        self._toggle_tapped()

class Opportunist(Spell):
    def __init__(self, artwork):
        super(Opportunist, self).__init__()
        self.name = 'Opportunist'
        self.color = 'Orange'
        self.description = 'Ready spell from linked room'
        self.artwork = artwork

    def cast(self, board):
        self._validate_spell_status(board)

        eligible_spells = []
        for spell in board.spells:
            if spell.faction == board.faction and spell.tapped:
                # TODO: verify spell's room is linked to the Opportunist
                eligible_spells.append(spell)
        spell = choose_from_list(
            board.screen,
            eligible_spells,
            prompt_text='Choose spell to untap:'
        )
        if not spell:
            raise InvalidMove('There are no linked untapped spells')

        spell.tapped = False
        self._toggle_tapped()

class Overwork(Spell):
    def __init__(self):
        super(Overwork, self).__init__() # initializes faction and tapped
        self.name = 'Overwork'
        self.color = 'Orange'
        self.description = 'Gain one action per adjacent object'

    def cast(self, board):
        self._validate_spell_status(board)
        adj_hexes = location.find_adjacent_hexes(board, board.get_current_player().hex)
        board.actions += len([x for x in adj_hexes if x.occupant])
        self._toggle_tapped()

class Usurper(Spell):
    def __init__(self, artwork):
        super(Usurper, self).__init__() # initializes faction and tapped
        self.name = 'Usurper'
        self.color = 'Umber'
        self.description = 'Shrink region twice, then grow twice'
        self.artwork = artwork

    def cast(self, board):
        self._validate_spell_status(board)
        self._toggle_tapped()
        # pick two linked hexes to flip
        for i in range(2):
            hex_to_flip = choose_hexes(
                board.screen,
                location.linked_hexes(board, self.artwork.hex),
                prompt_text = 'Click a {} aura to flip'.format(self.faction),
            )
            hex_to_flip.aura = other_faction(hex_to_flip.aura)
            board.flush_aura_data()
            # check to see if we flipped under the artwork/
            # if so, stop Usurping
            if self.artwork.hex.aura != board.faction:
                return None
        for i in range(2):
            hex_to_change = choose_hexes(
                board.screen,
                location.adjacent_linked_region(board, self.artwork.hex),
                prompt_text = 'Click a hex on which to grow',
            )
            hex_to_change.aura = board.faction
            board.flush_aura_data()

class Upset(Spell):
    def __init__(self):
        super(Upset, self).__init__() # initializes faction and tapped
        self.name = 'Upset '
        self.color = 'Umber'
        self.description = 'Rearrange auras under & around self'

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
    
    def cast(self, board):
        self._validate_artwork_status(board)
        moving_room = choose_from_list(
            board.screen,
            location.linked_rooms(board, self.artwork.hex),
            prompt_text="Choose a linked room to move:"
        )
        board.screen.info.text = "Arrow keys move Room {}. \',\' and \'.\' rotate. Enter to finish.".format(moving_room)
        finished_with_stonemason = False
        
        while not(finished_with_stonemason):
            key = get_keypress(board.screen)
            if key == "return":
                #check to see if no hexes overlap
                finished_with_stonemason = True
                #check for collisions
                all_hexes = board.get_all_hexes()
                for moving_hex in moving_room.hexes:
                    counter = 0
                    for hex in all_hexes:
                        if location.hexes_colocated(moving_hex, hex):
                            counter += 1
                    if counter > 1:
                        finished_with_stonemason = False
                        board.screen.info.error = "Overlaps are death."
                        break
                # TODO: CHECK CONNECTIVITY RULES
                if not board.connectivity_test():
                    board.screen.info.error = "Board fails connectivity rules."
                    finished_with_stonemason = False
            elif key == "left":
                moving_room.translate(np.matrix([0,-1,1]))
            elif key == "right":
                moving_room.translate(np.matrix([0,1,-1]))
            elif key == "up":
                moving_room.translate(np.matrix([-1,0,1]))
            elif key == "down":
                moving_room.translate(np.matrix([1,0,-1]))
            elif key == ",":
                moving_room.rotate(1)
            elif key == ".":
                moving_room.rotate(int(-1))
            board.flush_hex_data()
            board.flush_gamepieces()
        board.screen.info.error = ""
        self._toggle_tapped()
        

class Shovel(Spell):
    def __init__(self):
        super(Shovel, self).__init__() # initializes faction and tapped
        self.name = 'Shovel'
        self.color = 'Sapphire'
        self.description = "Move Shovel room to adjacent space, or if you\'re on the Shovel move it anywhere"

    def create_Shovel_room(self, location):
        return Room("Shovel",
            location, [],
            None, None
            )

    def cast(self, board):
        self._validate_spell_status(board)

        # check if the shovel has been placed yet
        shovel_is_placed = any([room.name == "Shovel" for room in board.rooms])
        if shovel_is_placed:
            shovel_index = [index for index,room in enumerate(board.rooms) if room.name == "Shovel"][0]
            player_on_shovel = (board.rooms[shovel_index].hexes[0].occupant == board.get_current_player())
        if shovel_is_placed and player_on_shovel:
            # time to move the shovel!
            
            # get a list of all possible Shovel locations
            # if the player is not on the shovel,
            new_hex_locations = location.find_unoccupied_neighbors(board, board.get_all_hexes())  
        else:
            # make temporary room with hexes adjacent to current player
            player_hex = board.get_current_player().hex
            new_hex_locations = location.find_unoccupied_neighbors(board,[player_hex])
            # make room with hexes at new_hex_locations, and choose from them
            if new_hex_locations == []:
                raise InvalidMove("There's nowhere to place the Shovel")
     
        # make a temporary room with these locations.
        board.rooms.append(Room("Temp",
            None,
            new_hex_locations,None,None,relative_shape=False)
        )
        # get the (possibly first-ever) location for the Shoel
        board.flush_hex_data()
        shovel_location = choose_hexes(
            board.screen,
            board.rooms[-1].hexes,
            prompt_text = "Choose where the Shovel will go"
        ).location
        #get rid of the temporary room
        board.rooms.pop()
        if not(shovel_is_placed):
            board.rooms.append(self.create_Shovel_room(shovel_location))
        else:
            board.rooms[shovel_index].hexes[0].location = shovel_location
        board.flush_hex_data()
        self._toggle_tapped()

class Locksmith(Spell):
    def __init__(self, artwork):
        super(Locksmith, self).__init__() # initializes faction and tapped
        self.name = 'Locksmith'
        self.color = 'Lime'
        self.description = 'Move linked object anywhere'
        self.artwork = artwork

    def cast(self, board):
        self._validate_spell_status(board)
        # get list of linked objects
        linked_hexes = location.linked_hexes(board, self.artwork.hex)
        linked_objects = [hex.occupant for hex in linked_hexes if hex.occupant]

        # get list of hexes to move to from the board
        target_hexes = [hex for hex in board.get_all_hexes() if not(hex.occupant)]
        if target_hexes == []:
            raise InvalidMove('All hexes are occupied.')

        # choose a linked object to move. There should always be at least one,
        # since we've validated that the Locksmith is on an aura
        target_object = choose_from_list(
            board.screen,
            linked_objects,
            prompt_text='Choose object to move:',
        )
        target_hex = choose_hexes(
            board.screen,
            target_hexes,
            prompt_text='Click where to move {}'.format(target_object)
        )
        board.move_object(target_object, from_hex = target_object.hex, to_hex = target_hex)
        self._toggle_tapped()

class Leap(Spell):
    def __init__(self):
        super(Leap, self).__init__() # initializes faction and tapped
        self.name = 'Leap  '
        self.color = 'Lime'
        self.description = 'Trade places with object in row'

    def cast(self, board):
        self._validate_spell_status(board)

        current_player = board.get_current_player()

        # get list of leap-able objects
        leapable_objects = []
        for obj in board.get_placed_non_player_objects():
            if location.leap_eligible(board, current_player.hex, obj.hex):
                leapable_objects.append(obj)

        target_object = choose_from_list(
            board.screen,
            leapable_objects,
            'Choose an object to Leap with:',
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
                    target_hex_index = choose_hexes(
                        board.screen,
                        [location.find_hex(board,loc) for loc in unoccupied_locations],
                        prompt_text="Click a hex to place {}".format(hex.occupant),
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

    def cast(self, board):
        self._validate_spell_status(board)
        current_player = board.get_current_player()

        # get target object for yoking
        target_object = choose_from_list(
            board.screen,
            board.get_placed_non_player_objects(),
            'Pick an object to Yoke with:',
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
        player_direction = choose_hexes(
            board.screen,
            [x[0] for x in possible_location_data],
            prompt_text="Choose the destination of the player:"
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

"""
Helper method to place auras on hexes, used in Imposter and Upset.

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
        new_hex = choose_hexes(
            board.screen,
            [hex for hex in hex_list if not hex.aura],
            prompt_text = "Click a hex for aura {}. Auras remaining: {}".format(aura, remaining_auras),
        )
        new_hex.aura = aura
        board.flush_aura_data()
