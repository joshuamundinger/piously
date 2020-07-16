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

# TODO: make more things allow clicking (either replace keypress or allow both)
#  - Leap + Locksmith choose_from_list to pick what obj to move
#  - behavior questions:
#     - [done] can leave shovel floating? (now=no) > NO
#     - [done] can imposter onto shovel? (now=yes) > YES (but you'd never want to)
#     - [done] can imposter from shovel? (now=yes) > YES (places 3 nones + shovel aura)
#     - can stonemason the shovel (now=yes)
# - test edge cases:
#     - [done] Imposter with Shovel

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
    def _validate_spell_status_and_tap(self, board):
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

        # mark spell used
        self.tapped = True

    def _validate_artwork_status(self, board):
        # if the spell has an artwork, check if it's placed on the board, on your aura
        if self.artwork:
            if self.artwork.hex:
                if self.artwork.hex.aura != board.faction:
                    raise InvalidMove('{} artwork is not on player\'s aura'.format(self.name))
            else:
                raise InvalidMove('{} artwork is not placed on board'.format(self.name))

    # TODO: verify all returns call this method
    def _exit_cast(self, done):
        if done:
            self.tapped = True
        else:
            self.tapped = False
        return done

class Priestess(Spell):
    def __init__(self, artwork):
        super(Priestess, self).__init__()
        self.name = 'Priestess'
        self.color = 'Pink'
        self.description = 'Grow linked region'
        self.artwork = artwork

    def cast(self, board):
        self._validate_spell_status_and_tap(board)

        # choose the hex to bless
        adjacent_linked_hexes = location.adjacent_linked_region(board, board.artworks[0].hex)
        target_hex = choose_hexes(
            board.screen,
            adjacent_linked_hexes,
            prompt_text = 'Click hex to grow linked region',
            error_text = 'There are no hexes which the Priestess may bless',
        )
        if not target_hex:
            return self._exit_cast(done=False)

        target_hex.aura = board.faction
        return self._exit_cast(done=True)

class Purify(Spell):
    def __init__(self):
        super(Purify, self).__init__()
        self.name = 'Purify'
        self.color = 'Pink'
        self.description = 'Bless underneath adjacent object'

    def cast(self, board):
        self._validate_spell_status_and_tap(board)
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
            return self._exit_cast(done=False)

        hex.aura = board.faction
        return self._exit_cast(done=True)

class Imposter(Spell):
    def __init__(self, artwork):
        super(Imposter, self).__init__()
        self.name = 'Imposter'
        self.color = 'Indigo'
        self.description = 'Copy auras from Imposter\'s room to linked room'
        self.artwork = artwork

    def cast(self, board):
        validated = board.screen.choice(1)
        if not validated:
            self._validate_spell_status_and_tap(board)
            board.screen.choices.append(True)

        # get a linked room.
        target_room = board.screen.choice(2) or choose_from_list(
            board.screen,
            location.linked_rooms(board, self.artwork.hex),
            prompt_text = 'Choose room to copy to:',
        )
        if target_room == None:
            return self._exit_cast(done=False)
        # get list of auras in artwork's room
        aura_list = [hex.aura for hex in self.artwork.hex.room.hexes if hex.aura]

        # deal with shovel seperately since this could mean trying to put >1 aura on 1 hex
        if target_room.name == 'Shovel':
            if len(aura_list) == 0:
                pass
            elif 'Dark' in aura_list and 'Light' in aura_list:
                aura = choose_from_list(
                    board.screen,
                    ['Dark', 'Light'],
                    prompt_text = 'Choose aura for Shovel:',
                )
                if aura == None:
                    return self._exit_cast(done=False)
                target_room.hexes[0].aura = aura
            else:
                # all the auras are the same (there may only be one)
                target_room.hexes[0].aura = aura_list[0]
            return self._exit_cast(done=True)

        if place_auras_on_hexes(board, self, aura_list, target_room.hexes, 3):
            return self._exit_cast(done=True)
        return self._exit_cast(done=False)

class Imprint(Spell):
    def __init__(self):
        super(Imprint, self).__init__()
        self.name = 'Imprint'
        self.color = 'Indigo'
        self.description = 'Copy auras from around enemy to self'

    def cast(self, board):
        self._validate_spell_status_and_tap(board)

        # requires no input from player
        # get auras around opponent
        current_player = board.get_current_player()
        opposing_player = board.get_opposing_player()
        opposing_neighboring_auras = []
        for hex in location.find_adjacent_hexes(board, opposing_player.hex, return_nones=True):
            if hex:
                opposing_neighboring_auras.append(hex.aura)
            else:
                opposing_neighboring_auras.append(None)

        # now put auras on neighborhood of current_player, but don't copy Nones
        if opposing_player.hex.aura:
            current_player.hex.aura = opposing_player.hex.aura
        current_player_neighborhood = location.find_adjacent_hexes(
            board,
            current_player.hex,
            return_nones = True,
        )
        for i in range(6):
            if opposing_neighboring_auras[i] != None and current_player_neighborhood[i]:
                current_player_neighborhood[i].aura = opposing_neighboring_auras[i]
        return self._exit_cast(done=True)

class Opportunist(Spell):
    def __init__(self, artwork):
        super(Opportunist, self).__init__()
        self.name = 'Opportunist'
        self.color = 'Orange'
        self.description = 'Reuse spell from linked room'
        self.artwork = artwork

    def cast(self, board):
        self._validate_spell_status_and_tap(board)

        rooms_names = [room.color_name() for room in location.linked_rooms(board, self.artwork.hex)]

        eligible_spells = []
        for spell in board.spells:
            if spell.faction == board.faction and spell.tapped and \
                    spell != self and spell.name[0] in rooms_names:
                eligible_spells.append(spell)

        spell = choose_from_list(
            board.screen,
            eligible_spells,
            prompt_text = 'Choose spell to reuse:',
            error_text = 'There are no linked used spells',
            all_spells = board.spells,
        )
        if not spell:
            return self._exit_cast(done=False)

        spell.untap()

        return self._exit_cast(done=True)

class Overwork(Spell):
    def __init__(self):
        super(Overwork, self).__init__()
        self.name = 'Overwork'
        self.color = 'Orange'
        self.description = 'Gain one action per adjacent object'

    def cast(self, board):
        self._validate_spell_status_and_tap(board)
        adj_hexes = location.find_adjacent_hexes(board, board.get_current_player().hex)
        board.actions += len([x for x in adj_hexes if x.occupant])
        return self._exit_cast(done=True)

class Usurper(Spell):
    def __init__(self, artwork):
        super(Usurper, self).__init__()
        self.name = 'Usurper'
        self.color = 'Umber'
        self.description = 'Shrink region twice, then grow twice'
        self.artwork = artwork

    def cast(self, board):
        self._validate_spell_status_and_tap(board)
        # pick two linked hexes to flip
        for i in range(2):
            prev_choice = board.screen.choice(1 + i)
            if prev_choice == None:
                hex_to_flip = choose_hexes(
                    board.screen,
                    location.linked_hexes(board, self.artwork.hex),
                    prompt_text = 'Click a {} aura to flip'.format(self.faction),
                )
                if hex_to_flip == None:
                    return self._exit_cast(done=False)
                hex_to_flip.aura = other_faction(hex_to_flip.aura)
                board.flush_aura_data()
                # check to see if we flipped under the artwork/
                # if so, stop Usurping
                if self.artwork.hex.aura != board.faction:
                    return self._exit_cast(done=True)
        for i in range(2):
            prev_choice = board.screen.choice(3 + i)
            if prev_choice == None:
                hex_to_change = board.screen.choice(3 + i) or choose_hexes(
                    board.screen,
                    location.adjacent_linked_region(board, self.artwork.hex),
                    prompt_text = 'Click a hex on which to grow',
                )
                if hex_to_change == None:
                    return self._exit_cast(done=False)
                hex_to_change.aura = board.faction
                board.flush_aura_data()
        return self._exit_cast(done=True)

class Upset(Spell):
    def __init__(self):
        super(Upset, self).__init__()
        self.name = 'Upset'
        self.color = 'Umber'
        self.description = 'Rearrange auras under & around self'

    def cast(self, board):
        self._validate_spell_status_and_tap(board)
        # get neighborhood of 7 hexes and their auras
        neighborhood = location.find_adjacent_hexes(board, board.get_current_player().hex)
        neighborhood.append(board.get_current_player().hex)
        # get auras on neighborhood
        aura_list = [x.aura for x in neighborhood if x.aura]
        # rearrange auras in neighborhood
        if place_auras_on_hexes(board, self, aura_list, neighborhood, 1):
            return self._exit_cast(done=True)
        return self._exit_cast(done=False)

class Stonemason(Spell):
    def __init__(self, artwork):
        super(Stonemason, self).__init__()
        self.name = 'Stonemason'
        self.color = 'Sapphire'
        self.description = 'Move linked room anywhere'
        self.artwork = artwork

    def cast(self, board):
        self._validate_artwork_status(board)
        board.check_game_over = False

        moving_room = board.screen.choice(1) or choose_from_list(
            board.screen,
            location.linked_rooms(board, self.artwork.hex),
            prompt_text="Choose a linked room to move:"
        )
        if moving_room == None:
            return self._exit_cast(done=False)

        board.screen.info.text = "Arrow keys move Room {}. < , > and < . > rotate. Enter to finish.".format(moving_room)
        finished_with_stonemason = False

        while not(finished_with_stonemason):
            key = get_keypress(board.screen)
            if key == None:
                return self._exit_cast(done=False)
            elif key == "return" or key == "Enter":
                # check to see if no hexes overlap
                finished_with_stonemason = True
                # check moving_room for collisions
                if board.check_for_collisions(moving_room):
                    finished_with_stonemason = False
                    board.screen.info.error = "Overlaps are death."
                if not board.connectivity_test():
                    board.screen.info.error = "Board fails connectivity rules:" \
                        + " Each room must be adjacent to at least two other rooms," \
                        + " and the whole temple must be connected"
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
        board.check_game_over = True
        return self._exit_cast(done=True)

class Shovel(Spell):
    def __init__(self):
        super(Shovel, self).__init__()
        self.name = 'Shovel'
        self.color = 'Sapphire'
        self.description = "Move Shovel to adjacent space, or if you\'re on it move Shovel anywhere"

    def create_Shovel_room(self, location):
        return Room("Shovel",
            location, [],
            None, None
        )

    def cast(self, board):
        self._validate_spell_status_and_tap(board)

        # temp room represents all the places that the shovel can be placed
        temp_is_placed = any([room.name == "Temp" for room in board.rooms])
        shovel_room = next((room for room in board.rooms if room.name == "Shovel"), None)
        if not temp_is_placed:
            player_on_shovel = board.get_current_player().hex.room == shovel_room

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
            return self._exit_cast(done=False)
        shovel_location = shovel_hex.location

        # get rid of the temporary room
        board.rooms.pop()
        if shovel_room:
            shovel_room.hexes[0].location = shovel_location
        else:
            board.rooms.append(self.create_Shovel_room(shovel_location))

        board.flush_hex_data()
        return self._exit_cast(done=True)

class Locksmith(Spell):
    def __init__(self, artwork):
        super(Locksmith, self).__init__()
        self.name = 'Locksmith'
        self.color = 'Lime'
        self.description = 'Move linked object anywhere'
        self.artwork = artwork

    def cast(self, board):
        self._validate_spell_status_and_tap(board)
        # get list of linked objects
        linked_hexes = location.linked_hexes(board, self.artwork.hex)
        linked_objects = [hex.occupant for hex in linked_hexes if hex.occupant]

        # get list of hexes to move to from the board
        target_hexes = [hex for hex in board.get_all_hexes() if not(hex.occupant)]
        if target_hexes == []:
            # this cannot happen since there are only 9 possible occupants :)
            raise InvalidMove('All hexes are occupied.')

        # choose a linked object to move. There should always be at least one,
        # since we've validated that the Locksmith is on an aura
        target_object = board.screen.choice(1) or choose_from_list(
            board.screen,
            linked_objects,
            prompt_text='Choose object to move:',
        )
        if target_object == None:
            return self._exit_cast(done=False)

        target_hex = choose_hexes(
            board.screen,
            target_hexes,
            prompt_text='Click where to move {}'.format(target_object)
        )
        if target_hex == None:
            return self._exit_cast(done=False)

        board.move_object(target_object, from_hex = target_object.hex, to_hex = target_hex)
        return self._exit_cast(done=True)

class Leap(Spell):
    def __init__(self):
        super(Leap, self).__init__()
        self.name = 'Leap'
        self.color = 'Lime'
        self.description = 'Trade places with object in row'

    def cast(self, board):
        self._validate_spell_status_and_tap(board)

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
            return self._exit_cast(done=False)

        board.swap_object(current_player, target_object)
        return self._exit_cast(done=True)

class Yeoman(Spell):
    def __init__(self, artwork):
        super(Yeoman, self).__init__()
        self.name = 'Yeoman'
        self.color = 'Yellow'
        self.description = 'Rearrange objects in linked rooms'
        self.artwork = artwork

    # TODO: WARNING this code is has not been tested for pygame board
    def cast(self, board, str=[]):
        self._validate_artwork_status(board)

        linked_rooms = location.linked_rooms(board, self.artwork.hex)
        while True:
            # check if user is done casting
            board.screen.info.text = "Press enter to stop casting or any other key to contine" # TODO: remove
            board.flush_gamepieces()
            key = get_keypress(board.screen, enable_buttons = False)
            if key == "return" or key == "Enter":
                board.screen.action_buttons_on = True
                return self._exit_cast(done=True)

            object_locations = [hex for room in linked_rooms for hex in room.hexes if hex.occupant]
            from_hex = board.screen.choice(1) or choose_hexes(
                board.screen,
                object_locations,
                prompt_text = "Click an object to move or press enter to end",
            )
            if from_hex == None:
                return self._exit_cast(done=False)

            obj = from_hex.occupant
            to_hex = choose_hexes(
                board.screen,
                from_hex.room.hexes,
                prompt_text = "Click where to move {}".format(obj),
            )
            if to_hex == None:
                return self._exit_cast(done=False)

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
                return self._exit_cast(done=True)


class Yoke(Spell):
    def __init__(self):
        super(Yoke, self).__init__()
        self.name = 'Yoke'
        self.color = 'Yellow'
        self.description = 'Move self and object one space'

    def cast(self, board):
        self._validate_spell_status_and_tap(board)
        current_player = board.get_current_player()

        # get target object for yoking
        target_object = board.screen.choice(1) or choose_from_list(
            board.screen,
            board.get_placed_non_player_objects(),
            'Pick an object to Yoke with:',
            'There is no other object to Yoke',
        )
        if target_object == None:
            return self._exit_cast(done=False)

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
            return self._exit_cast(done=False)
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
        return self._exit_cast(done=True)

"""
Helper method to place auras on hexes, used in Imposter and Upset.

place_auras_on_hexes replaces the auras on the hexes in hex_list with
those in aura_list, based on user input

Params:
 - aura_list: list of auras to place (entries should be 'Dark' or 'Light'). None entries
    will automatically be removed
 - hex_list: list of hexes to put auras on
"""
def place_auras_on_hexes(board, spell, aura_list, hex_list, choice_idx):
    auras_to_place = board.screen.choice(choice_idx)
    if not auras_to_place:
         auras_to_place = [aura for aura in aura_list if aura] # remove Nones
         board.screen.choices.append(auras_to_place)

         # clear out existing auras on the hexes
         for hex in hex_list:
             hex.aura = None
         board.flush_aura_data()

    if len(auras_to_place) > len(hex_list):
        raise RuntimeError('Pidgeonhole Problem: tried to put too many auras on a set of hexes')

    all_auras = deepcopy(auras_to_place)
    for aura in all_auras:
        new_hex = choose_hexes(
            board.screen,
            [hex for hex in hex_list if not hex.aura],
            prompt_text = "Auras to place: {}. Click a hex for aura {}".format(
                ', '.join(auras_to_place),
                aura,
            ),
        )
        if new_hex == None:
            return spell._exit_cast(done=False)

        new_hex.aura = aura
        auras_to_place.remove(aura)
        board.flush_aura_data()

    return spell._exit_cast(done=True)
