"""
Board stores a full set of game state:
 - 7 Rooms with 4 Hexes each, and the Shovel
 - 14 Spells
 - 7 Artworks
 - 2 Players
 - the number of actions remaining for the current player
 - the faction of the current player
 - a graphics screen to send data to be displayed

 Creating a new board creates a full set of objects (Rooms, Spells, Artworks, Players)
"""
import numpy as np

from backend.artwork import Artwork
from backend.errors import InvalidMove
from backend.helpers import display_list, other_faction
from backend.location import neighboring_region, find_adjacent_rooms, hexes_colocated, linked_rooms
from backend.player import Player
from backend.room import Room
from backend.spell import (
    Priestess,
    Purify,
    Imposter,
    Imprint,
    Opportunist,
    Overwork,
    Usurper,
    Upset,
    Stonemason,
    Shovel,
    Locksmith,
    Leap,
    Yeoman,
    Yoke,
)
from copy import deepcopy

class Board(object):
    def __init__(self, screen, faction="Dark", actions=None, players=None, artworks=None, spells=None, rooms=None):
        self.screen = screen
        self.faction = faction
        self.actions = actions
        self.players = players or {
            'Dark': Player('Dark'),
            'Light': Player('Light'),
        }
        self.game_over = False
        self.check_game_over = True

        # IDEA: what if each Room inits it's spells and each a_spell inits its
        # artworks and neither are stored directly on board
        self.artworks = artworks or [
            Artwork('Priestess'),
            Artwork('Imposter'),
            Artwork('Opportunist'),
            Artwork('Usurper'),
            Artwork('Stonemason'),
            Artwork('Locksmith'),
            Artwork('Yeoman'),
        ]
        self.spells = spells or [
            Priestess(self.artworks[0]),
            Purify(),
            Imposter(self.artworks[1]),
            Imprint(),
            Opportunist(self.artworks[2]),
            Overwork(),
            Usurper(self.artworks[3]),
            Upset(),
            Stonemason(self.artworks[4]),
            Shovel(),
            Locksmith(self.artworks[5]),
            Leap(),
            Yeoman(self.artworks[6]),
            Yoke(),
        ]
        self.rooms = rooms or [
            Room('Pink', np.matrix([3,-4,1]),
                [   np.matrix([-1,0,1]),
                    np.matrix([-1,1,0]),
                    np.matrix([1,0,-1])
                ], self.spells[0], self.spells[1]
            ),
            Room('Indigo', np.matrix([3,-3,0]),
                [   np.matrix([1,0,-1]),
                    np.matrix([2,0,-2]),
                    np.matrix([3,0,-3])
                ], self.spells[2], self.spells[3]
            ),
            Room('Orange', np.matrix([2,-2,0]),
                [   np.matrix([0,1,-1]),
                    np.matrix([1,0,-1]),
                    np.matrix([1,1,-2])
                ],  self.spells[4], self.spells[5]
            ),
            Room('Umber', np.matrix([4,-2,-2]),
                [   np.matrix([0,1,-1]),
                    np.matrix([-1,2,-1]),
                    np.matrix([-2,2,0])
                ],  self.spells[6],self.spells[7]
            ),
            Room('Sapphire', np.matrix([0,0,0]),
                [   np.matrix([1,0,-1]),
                    np.matrix([1,1,-2]),
                    np.matrix([2,1,-3])
                ],  self.spells[8], self.spells[9]
            ),
            Room('Lime', np.matrix([1,2,-3]),
                [   np.matrix([1,0,-1]),
                    np.matrix([2,0,-2]),
                    np.matrix([2,1,-3])
                ], self.spells[10], self.spells[11]
            ),
            Room('Yellow', np.matrix([0,3,-3]),
                [   np.matrix([0,-1,1]),
                    np.matrix([-1,1,0]),
                    np.matrix([1,0,-1])
                ], self.spells[12], self.spells[13]
            )
        ]

    def __str__(self):
        return '\n***BOARD***\n{overview}\nplayers:{players}\nartworks:{artworks}\n'.format(
            overview = self.get_state_msg(),
            players = display_list(self.players.values()),
            artworks = display_list(self.artworks),
        )

    def __deepcopy__(self, memo):
        return Board(
            self.screen,
            self.faction,
            self.actions,
            deepcopy(self.players, memo),
            deepcopy(self.artworks, memo),
            deepcopy(self.spells, memo),
            deepcopy(self.rooms, memo),
        )

    def get_current_player(self):
        return self.players[self.faction]

    def get_opposing_player(self):
        return self.players[other_faction(self.faction)]

    def get_state_msg(self):
        turn = '{}\'s turn'.format(self.faction)
        actions = '{} action{} left'.format(
            self.actions,
            '' if self.actions == 1 else 's',
        )
        return '{}, {}'.format(turn, actions)

    def get_placed_objects(self):
        # return all objects currently placed on board
        artworks = [art for art in self.artworks if art.hex]
        players = [player for player in self.players.values() if player.hex]
        return artworks + players

    def get_placed_non_player_objects(self):
        return [obj for obj in self.get_placed_objects() if obj != self.get_current_player()]

    def get_eligible_spells(self, include_unplaced=False):
        eligible_spells = []
        for spell in self.spells:
            # check player owns spell and hasn't already used it
            if spell.faction != self.faction:
                continue
            elif spell.tapped:
                continue

            # if spell has artwork, it should be placed on the player's aura
            if spell.artwork:
                if not spell.artwork.hex:
                    if not include_unplaced:
                        continue
                elif spell.artwork.hex.aura != self.faction:
                    continue

            eligible_spells.append(spell)

        return eligible_spells

    def is_game_over(self):
        if not self.check_game_over:
            return False
        # for each aura'd hex in a room, check if the linked region has all seven rooms.
        winners = []
        for hex in self.rooms[0].hexes:
            if hex.aura:
                linked = linked_rooms(self, hex, include_shovel=False)
                if len(linked) == 7:
                    winners.append(hex.aura)
        win_set = set(winners)
        if not win_set:
            return None
        elif len(win_set) == 1:
            return winners[0]
        else:
            return "Tie"

    ########################
    # board layout methods #
    ########################

    def get_room(self, hex):
        # find the room containing the given hex
        rooms = [room for room in self.rooms if hex in room.hexes]
        if len(rooms) == 1:
            return rooms[0]
        else:
            return rooms

    def get_neighboring_rooms(self, starting_room):
        neighboring_rooms = []
        for current_hex in neighboring_region(self, starting_room):
            current_room = self.get_room(current_hex)
            if not(current_room in neighboring_rooms):
                neighboring_rooms.append(current_room)
        return neighboring_rooms

    def connectivity_test(self):
        for room in self.rooms:
            neighbors = find_adjacent_rooms(self, room, include_shovel=False)
            if room.name == 'Shovel' and len(neighbors) < 1:
                return False
            elif room.name != 'Shovel' and len(neighbors) < 2:
                return False
        return True

    #returns whether room collides with another room in the board
    def check_for_collisions(self, room):
        all_hexes = self.get_all_hexes()
        for moving_hex in room.hexes:
            counter = 0
            for hex in all_hexes:
                if hexes_colocated(moving_hex, hex):
                    counter += 1
            if counter > 1:
                return True
        return False


    ############################
    # dynamic gameplay methods #
    ############################

    def end_turn(self, actions=3):
        """Reset board values for start of new turn"""
        self.actions = actions
        [spell.untap() for spell in self.spells]
        self.faction = other_faction(self.faction)

    def move_object(self, occupant, from_hex=None, to_hex=None):
            # order matters here, updating occupant.hex last makes it ok for
            #from_hex to be occupant.hex initially
            if from_hex != None:
                from_hex.occupant = None
            if to_hex != None:
                if to_hex.occupant != None:
                    raise InvalidMove('You\'re trying to move onto an occupied hex.')
                to_hex.occupant = occupant
            occupant.hex = to_hex

    def swap_object(self, object1, object2):
        hex_1 = object1.hex
        object1.hex = object2.hex
        object2.hex = hex_1
        object2.hex.occupant = object2
        object1.hex.occupant = object1

    def get_all_hexes(self):
            # returns a list of all hexes
            hex_list = []
            for room in self.rooms:
                hex_list += room.hexes
            return hex_list
    ##############################
    # flush display data methods #
    ##############################

    def flush_hex_data(self):
        hex_maps = []
        for hex in self.get_all_hexes():
            hex_maps.append({
                'x': hex.location.flat[0],
                'y': hex.location.flat[1],
                'room': hex.room.color_name(),
            })
        self.screen.make_map(hex_maps)

    def return_hex_data(self):
        hex_maps = []
        for room in self.rooms:
            for hex in room.hexes:
                if hex.occupant:
                    type = hex.occupant.get_type()
                    color = hex.occupant.get_color()
                    name = str(hex.occupant)
                else:
                    type = None
                    color = None
                    name = None

                hex_maps.append({
                    'x': int(hex.location.flat[0]),
                    'y': int(hex.location.flat[1]),
                    'room': hex.room.name,
                    'room_color': hex.room.color_name(),
                    'obj_color': color,
                    'obj_type': type,
                    'obj_name': name,
                    'aura_color': hex.aura,
                    'active': not self.game_over and hex in self.screen.active_hexes,
                })
        return hex_maps

    def return_spell_data(self):
        data = []
        active_spells = self.get_eligible_spells(include_unplaced=True)
        for spell in self.spells:
            data.append({
                'name': spell.name,
                'faction': spell.faction,
                'tapped': spell.tapped,
                'has_artwork': bool(spell.artwork),
                'unplaced_artwork': bool(spell.artwork and not spell.artwork.hex),
                'active': not self.game_over and spell in active_spells,
            })
        return data

    def flush_spell_data(self):
        data = []
        for spell in self.spells:
            data.append({
                'name': spell.name,
                'description': spell.description,
                'faction': spell.faction,
                'tapped': spell.tapped,
                'artwork': bool(spell.artwork and not spell.artwork.hex)
            })
        self.screen.make_spells(data)

    def flush_player_data(self):
        data = []
        for player in self.players.values():
            if player.hex:
                data.append({
                    'x': player.hex.location.flat[0],
                    'y': player.hex.location.flat[1],
                    'faction': player.faction,
                })
        self.screen.player_data = data

    def flush_artwork_data(self):
        data = []
        for artwork in self.artworks:
            if artwork.hex:
                data.append({
                    'x': artwork.hex.location.flat[0],
                    'y': artwork.hex.location.flat[1],
                    'room': artwork.color[0],
                })
        self.screen.artwork_data = data

    def flush_aura_data(self):
        data = []
        for hex in self.get_all_hexes():
            if hex.aura:
                data.append({
                    'x': hex.location.flat[0],
                    'y': hex.location.flat[1],
                    'faction': hex.aura,
                })
        self.screen.aura_data = data

    def flush_gamepieces(self):
        self.flush_aura_data()
        self.flush_player_data()
        self.flush_artwork_data()
        self.flush_spell_data()
        self.screen.board_state.text = '{}\'s turn'.format(self.faction)
        self.screen.board_state.error = '{} action{} left'.format(
            self.actions,
            '' if self.actions == 1 else 's',
        )
