"""
This file defines the Spell class and 14 Spell subclasses each of
which implement cast(), which is the main method that encodes Spell behavior.

Each Spell includes a name, description, who owns it, whether it has been used this turn,
and may have a pointer to an associated artwork.
"""
from backend.errors import InvalidMove
from backend.helpers import other_faction
from backend.room import Room
# from graphics.pygame_input import choose_from_list, choose_hexes, get_keypress
from graphics.js_input import choose_from_list, choose_hexes, get_keypress
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
            prompt_text = 'Click hex to grow linked region',
            error_text = 'There are no hexes which the Priestess may bless',
        )
        if not target_hex:
            return False

        target_hex.aura = board.faction
        self._toggle_tapped()
        return True

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
            error_text = 'No hexes to Purify',
        )
        if not hex:
            return False

        hex.aura = board.faction
        self._toggle_tapped()
        return True

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
        target_room = board.screen.choice(1) or choose_from_list(
            board.screen,
            location.linked_rooms(board, self.artwork.hex),
            prompt_text = 'Choose room to copy to:',
        )
        if target_room == None:
            return False
        # get list of auras in artwork's room
        aura_list = [hex.aura for hex in self.artwork.hex.room.hexes if hex.aura]
        # TODO: handle if you are copying more than one aura onto the Shovel
        print('about to place')
        if place_auras_on_hexes(board, aura_list, target_room.hexes, 2):
            self._toggle_tapped()
            return True
        return False

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
        return True

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
            prompt_text = 'Choose spell to untap:',
            error_text = 'There are no linked untapped spells',
            all_spells = board.spells,
        )
        if not spell:
            return False

        spell.tapped = False
        self._toggle_tapped()
        return True

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
        return True

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
            hex_to_flip = board.screen.choice(1 + i) or choose_hexes(
                board.screen,
                location.linked_hexes(board, self.artwork.hex),
                prompt_text = 'Click a {} aura to flip'.format(self.faction),
            )
            if hex_to_flip == None:
                return False
            hex_to_flip.aura = other_faction(hex_to_flip.aura)
            board.flush_aura_data()
            # check to see if we flipped under the artwork/
            # if so, stop Usurping
            if self.artwork.hex.aura != board.faction:
                return True
        for i in range(2):
            hex_to_change = board.screen.choice(3 + i) or choose_hexes(
                board.screen,
                location.adjacent_linked_region(board, self.artwork.hex),
                prompt_text = 'Click a hex on which to grow',
            )
            if hex_to_change == None:
                return False
            hex_to_change.aura = board.faction
            board.flush_aura_data()
        return True

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
        if place_auras_on_hexes(board, aura_list, neighborhood, 1):
            self._toggle_tapped()
            return True
        return False

class Stonemason(Spell):
    def __init__(self, artwork):
        super(Stonemason, self).__init__() # initializes faction and tapped
        self.name = 'Stonemason'
        self.color = 'Sapphire'
        self.description = 'Move linked room anywhere'
        self.artwork = artwork

    def cast(self, board):
        self._validate_artwork_status(board)

        moving_room = board.screen.choice(1) or choose_from_list(
            board.screen,
            location.linked_rooms(board, self.artwork.hex),
            prompt_text="Choose a linked room to move:"
        )
        if moving_room == None:
            return False

        board.screen.info.text = "Arrow keys move Room {}. < , > and < . > rotate. Enter to finish.".format(moving_room)
        finished_with_stonemason = False

        while not(finished_with_stonemason):
            key = get_keypress(board.screen)
            if key == None:
                return False
            elif key == "return" or key == "Enter":
                # check to see if no hexes overlap
                finished_with_stonemason = True
                # check moving_room for collisions
                if board.check_for_collisions(moving_room):
                    finished_with_stonemason = False
                    board.screen.info.error = "Overlaps are death."
                # TODO: CHECK CONNECTIVITY RULES
                #  - I was able to leave the shovel floating
                if not board.connectivity_test():
                    board.screen.info.error = "Board fails connectivity rules."
                    finished_with_stonemason = False
            else:
                moving_room.keyboard_movement(key)
            board.flush_hex_data()
            board.flush_gamepieces()

            # For js need to get rid of the old keypress, pygame will give AttributeError
            try:
                if 'current_keypress' in board.screen.data:
                    board.screen.data.pop('current_keypress')
            except AttributeError:
                pass

        board.screen.info.error = ""
        self._toggle_tapped()
        return True

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

        # temp room represents all the places that the shovel can be placed
        temp_is_placed = any([room.name == "Temp" for room in board.rooms])
        shovel_room = next((room for room in board.rooms if room.name == "Shovel"), None)
        print('temp placed: {}, shovel placed: {}'.format(temp_is_placed, bool(shovel_room)))
        if not temp_is_placed:
            player_on_shovel = board.get_current_player().hex.room == shovel_room
            print('on shovel', player_on_shovel)

            if player_on_shovel:
                # shovel can move anywhere - get neighbors of the whole board
                temp_locations = location.find_unoccupied_neighbors(board, board.get_all_hexes())
            else:
                # shovel can move to adjacent spots that are empty - get player's neighbors
                player_hex = board.get_current_player().hex
                temp_locations = location.find_unoccupied_neighbors(board,[player_hex])
                if temp_locations == []:
                    raise InvalidMove("There's nowhere to place the Shovel")

            # make a temporary room with these locations
            board.rooms.append(Room(
                name = "Temp",
                root = None,
                shape = temp_locations,
                a_spell = None,
                b_spell = None,
                relative_shape = False,
            ))

        # get the (possibly first-ever) location for the Shovel
        board.flush_hex_data()
        shovel_hex = choose_hexes(
            board.screen,
            board.rooms[-1].hexes,
            prompt_text = "Choose where the Shovel will go"
        )
        if shovel_hex == None:
            return False
        shovel_location = shovel_hex.location

        # get rid of the temporary room
        board.rooms.pop()
        if shovel_room:
            shovel_room.hexes[0].location = shovel_location
        else:
            board.rooms.append(self.create_Shovel_room(shovel_location))

        board.flush_hex_data()
        self._toggle_tapped()
        return True

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
        target_object = board.screen.choice(1) or choose_from_list(
            board.screen,
            linked_objects,
            prompt_text='Choose object to move:',
        )
        if target_object == None:
            return False

        target_hex = choose_hexes(
            board.screen,
            target_hexes,
            prompt_text='Click where to move {}'.format(target_object)
        )
        if target_hex == None:
            return False

        board.move_object(target_object, from_hex = target_object.hex, to_hex = target_hex)
        self._toggle_tapped()
        return True

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
            'There\'s no object to Leap with',
        )
        if not target_object:
            return False

        board.swap_object(current_player, target_object)
        # TODO: test
        self._toggle_tapped()
        return True

class Yeoman(Spell):
    def __init__(self, artwork):
        super(Yeoman, self).__init__() # initializes faction and tapped
        self.name = 'Yeoman'
        self.color = 'Yellow'
        self.description = 'Rearrange objects in linked rooms'
        self.artwork = artwork

    # TODO: WARNING this code is has not been tested for pygame board
    def cast(self, board, str=[]):
        choice_idx = 1
        self._validate_artwork_status(board)

        linked_rooms = location.linked_rooms(board, self.artwork.hex)
        while True:
            # check if user is done casting
            board.screen.info.text = "Press enter to stop casting or any other key to contine" # TODO: remove
            board.flush_gamepieces()
            key = get_keypress(board.screen, enable_buttons = False)
            if key == "return" or key == "Enter":
                board.screen.action_buttons_on = True
                self._toggle_tapped()
                return True

            object_locations = [hex for room in linked_rooms for hex in room.hexes if hex.occupant]
            from_hex = board.screen.choice(1) or choose_hexes(
                board.screen,
                object_locations,
                prompt_text = "Click an object to move or press enter to end",
            )
            if from_hex == None:
                return False

            obj = from_hex.occupant
            to_hex = choose_hexes(
                board.screen,
                from_hex.room.hexes,
                prompt_text = "Click where to move {}".format(obj),
            )
            if to_hex == None:
                return False

            if to_hex.occupant:
                board.swap_object(obj, to_hex.occupant)
            else:
                board.move_object(obj, from_hex, to_hex)

            # clear out stored choices beyond the first one if there are any
            if board.screen.choice(1):
                board.screen.choices = board.screen.choices[:1]

            # if yeoman is no longer on hex stop casting
            if self.artwork.hex.aura != board.faction:
                board.screen.info.error = 'Yeomen no longer on {} aura. Ending cast.'.format(board.faction)
                board.screen.action_buttons_on = True
                self._toggle_tapped()
                return True


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
        target_object = board.screen.choice(1) or choose_from_list(
            board.screen,
            board.get_placed_non_player_objects(),
            'Pick an object to Yoke with:',
            'There is no other object to Yoke',
        )
        if target_object == None:
            return False

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
            prompt_text = "Choose the destination of the player:",
            error_text = 'These two objects have no common direction to move',
        )
        if player_direction == None:
            return False
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
        return True

"""
Helper method to place auras on hexes, used in Imposter and Upset.

place_auras_on_hexes replaces the auras on the hexes in hex_list with
those in aura_list, based on user input

Params:
 - aura_list: list of auras to place (entries should be 'Dark' or 'Light'). None entries
    will automatically be removed
 - hex_list: list of hexes to put auras on
"""
def place_auras_on_hexes(board, aura_list, hex_list, choice_idx):
    # clean the list of empty auras
    starting_auras = [hex.aura for hex in hex_list]
    aura_list = [aura for aura in aura_list if aura]
    if len(aura_list) > len(hex_list):
        raise RuntimeError('Pidgeonhole Problem: tried to put too many auras on a set of hexes')
    remaining_auras = deepcopy(aura_list)
    # clear auras in target room
    for hex in hex_list:
        hex.aura = None
    board.flush_aura_data()
    for aura in aura_list:
        new_hex = board.screen.choice(choice_idx) or choose_hexes(
            board.screen,
            [hex for hex in hex_list if not hex.aura],
            prompt_text = "Click a hex for aura {}. Auras remaining: {}".format(aura, remaining_auras),
        )
        if new_hex == None:
            # put auras back how they were
            # TODO: improve this for js screen, since reset here means it won't "flush" auras
            for i in range(len(hex_list)):
                hex_list[i].aura = starting_auras[i]
            return False
        choice_idx += 1
        remaining_auras.remove(aura)
        new_hex.aura = aura
        board.flush_aura_data()
    return True
