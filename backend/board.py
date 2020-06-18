"""
Overall board class to store past and current game state.
"""
import numpy as np

from backend.artwork import Artwork
from backend.helpers import display_list, other_faction
from backend.player import Player
from backend.room import Room
import backend.location as location
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

class Board(object):
    def __init__(self, start_faction):
        self.faction = start_faction
        self.players = {
            'Dark': Player('Dark'),
            'Light': Player('Light'),
        }
        self.actions = 3

        # IDEA: what if each Room inits it's spells and each a_spell inits it's artworks and neither are stored directly on board
        self.artworks = [
            Artwork('Pink  '), # weird spacing is intentional so that they print nicely with \t
            Artwork('Indigo'),
            Artwork('Orange'),
            Artwork('Umber '),
            Artwork('Sapphire'),
            Artwork('Lime  '),
            Artwork('Yellow'),
        ]
        self.spells = [
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
        self.rooms = [
            #P
            Room('P', np.matrix([0,0,0]),
                [   np.matrix([1,0,-1]),
                    np.matrix([0,1,-1]),
                    np.matrix([0,-1,1])
                ], self.spells[0], self.spells[1]),
            #I
            Room('I', np.matrix([2,-2,0]),
                [   np.matrix([0,1,-1]),
                    np.matrix([0,2,-2]),
                    np.matrix([0,3,-3])
                ], self.spells[2], self.spells[3])
        ]

    def __str__(self):
        return '\n***BOARD***\n{faction}\'s turn\nactions:{actions}\nplayers:{players}\nspells:{spells}\nartworks:{artworks}\n***********\n'.format(
            faction = self.faction,
            actions = self.actions,
            players = display_list(self.players.values()),
            spells = display_list(self.spells),
            artworks = display_list(self.artworks),
        )

    def get_current_player(self):
        return self.players[self.faction]

    def get_opposing_player(self):
        if self.faction == 'Light':
            return self.players['Dark']
        else:
            return self.players['Light']

    def get_placed_objects(self):
        # return all objects currently placed on board
        return [art for art in self.artworks if art.hex] + [player for player in self.players.values() if player.hex]

    def get_placed_non_player_objects(self):
        return [obj for obj in self.get_placed_objects() if obj != self.get_current_player]        

    ######################
    # board layout methods
    ######################
    """
    # It's not clear that this function has any use.
    def is_connected(self):
        # does a breath-first search from the 0th hex in the 0th room,
        # then checks if all hexes have been found this way.
        number_of_hexes = sum([len(room.hexes) for room in self.rooms])
        return number_of_hexes == len(linked_search(self, self.rooms[0].hexes[0], False, False))
    """

    def get_room(self, hex):
        # find the room containing the given hex
        rooms = [room for room in self.rooms if hex in room.hexes]
        if len(rooms) == 1:
            return rooms[0]
        else:
            return rooms

    def get_neighboring_rooms(self, starting_room):
        neighboring_rooms = []
        for current_hex in location.neighboring_region(self, starting_room):
            current_room = self.get_room(current_hex)
            if not(current_room in neighboring_rooms):
                neighboring_rooms.append(current_room)
        return neighboring_rooms

    def get_adjacent_hexes(self, hex):
        """
        Returns a list of 0-6 adjacent Hexes.
        (0 is only possible if you input the Shovel and it's not on the board)
        """
        print('WARNING: get_adjacent_hexes not implemented')
        return []

    def get_adjacent_rooms(self, room):
        """
        Returns a list of 0-6 adjacent Rooms.
        (0 is only possible if you input the Shovel and it's not on the board)
        """
        print('WARNING: get_adjacent_rooms not implemented')
        return []

    def get_linked_rooms(self, hex):
        """
        Returns a list of 0-6 linked Rooms.

        Never includes the Shovel.
        """
        print('WARNING: get_linked_rooms not implemented')
        return []

    def end_turn(self):
        """Reset board values for start of new turn"""
        self.actions = 3
        [spell.untap() for spell in self.spells]
        self.faction = other_faction(self.faction)

    ##########################
    # string to object methods
    ##########################

    """
    Params: string should be one of [1 5 q t a g z d l]
    Returns: corresponding Artwork or Player object
    """
    def str_to_occupant(self, string):
        if string == '1':
            return self.artworks[0]
        elif string == '5':
            return self.artworks[1]
        elif string == 'q':
            return self.artworks[2]
        elif string == 't':
            return self.artworks[3]
        elif string == 'a':
            return self.artworks[4]
        elif string == 'g':
            return self.artworks[5]
        elif string == 'z':
            return self.artworks[6]
        elif string == 'd':
            return self.players['Dark']
        elif string == 'l':
            return self.players['Light']
        else:
            raise NameError('Invalid occupant string {}'.format(string))

    """
    Params: string should be one of [12 56 qw ty as gh zx] (first one is artwork, second is bewitchment)
    Returns: corresponding Spell object
    """
    def str_to_spell(self, string):
        if string == '1':
            return self.spells[0]
        elif string == '2':
            return self.spells[1]
        elif string == '5':
            return self.spells[2]
        elif string == '6':
            return self.spells[3]
        elif string == 'q':
            return self.spells[4]
        elif string == 'w':
            return self.spells[5]
        elif string == 't':
            return self.spells[6]
        elif string == 'y':
            return self.spells[7]
        elif string == 'a':
            return self.spells[8]
        elif string == 's':
            return self.spells[9]
        elif string == 'g':
            return self.spells[10]
        elif string == 'h':
            return self.spells[11]
        elif string == 'z':
            return self.spells[12]
        elif string == 'x':
            return self.spells[13]
        else:
            raise NameError('Invalid spell string {}'.format(string))

    """
    Params: string should be one of [1234 5678 qwer tyui asdf ghjk zxcv b n]
     - TODO: consider instead encoding hexes like: p0 p1 p2 p3 i0 i1 i2 i3 ...
    Returns: corresponding Hex object
    """
    def str_to_hex(self, string):
        # P
        if string == '1':
            return self.rooms[0].hexes[0]
        elif string == '2':
            return self.rooms[0].hexes[1]
        elif string == '3':
            return self.rooms[0].hexes[2]
        elif string == '4':
            return self.rooms[0].hexes[3]
        # I
        elif string == '5':
            return self.rooms[1].hexes[0]
        elif string == '6':
            return self.rooms[1].hexes[1]
        elif string == '7':
            return self.rooms[1].hexes[2]
        elif string == '8':
            return self.rooms[1].hexes[3]
        # O
        elif string == 'q':
            return self.rooms[2].hexes[0]
        elif string == 'w':
            return self.rooms[2].hexes[1]
        elif string == 'e':
            return self.rooms[2].hexes[2]
        elif string == 'r':
            return self.rooms[2].hexes[3]
        # U
        elif string == 't':
            return self.rooms[3].hexes[0]
        elif string == 'y':
            return self.rooms[3].hexes[1]
        elif string == 'u':
            return self.rooms[3].hexes[2]
        elif string == 'i':
            return self.rooms[3].hexes[3]
        # S
        elif string == 'a':
            return self.rooms[4].hexes[0]
        elif string == 's':
            return self.rooms[4].hexes[1]
        elif string == 'd':
            return self.rooms[4].hexes[2]
        elif string == 'f':
            return self.rooms[4].hexes[3]
        # L
        elif string == 'g':
            return self.rooms[5].hexes[0]
        elif string == 'h':
            return self.rooms[5].hexes[1]
        elif string == 'j':
            return self.rooms[5].hexes[2]
        elif string == 'k':
            return self.rooms[5].hexes[3]
        # Y
        elif string == 'z':
            return self.rooms[6].hexes[0]
        elif string == 'x':
            return self.rooms[6].hexes[1]
        elif string == 'c':
            return self.rooms[6].hexes[2]
        elif string == 'v':
            return self.rooms[6].hexes[3]
        # others
        elif string == 'b': # shovel
            return self.rooms[7].hexes[0]
        elif string == 'n':
            return None
        else:
            raise NameError('Invalid hex string {}'.format(string))

if __name__ == "__main__":
    b = Board("Dark")
    b.actions -= 1
    # b.spells[4].cast(b, 'q')
    print(b)
    b.end_turn()
    print(b)
