"""
A location is a vector of three integers whose entries sum to zero.
This is implemented using numpy's array class
"""

import numpy as np
from backend.board import Board
from backend.errors import InvalidMove
from backend.hex import Hex

unit_directions = [
        np.matrix([1,0,-1]),
        np.matrix([-1,1,0]),
        np.matrix([0,-1,1]),
        np.matrix([-1,0,1]),
        np.matrix([1,-1,0]),
        np.matrix([0,1,-1])
    ]

def find_hex(board, location):
    #given a board and a location, return the hex at this location, or None if no hex exists
    for room in board.rooms:
        for hexa in room.hexes:
            if (hexa.location == location).all():
                return hexa
    return None

def find_adjacent_hexes(board, starting_hex):
    #given a hex, return the (up to six) neighboring hexes
    return [ item for item in  [find_hex(board, starting_hex.location + u) for u in unit_directions] if item != None]

def leap_eligible(board, hex1, hex2):
    #returns true if two pieces on hex1 and hex2 can Leap, and false otherwise
    try:
        displacement = hex1.location - hex2.location
    except AttributeError:
        print("You tried to leap, but passed nonexistent hexes or locations. Shame on you.")
        return False
    number_of_tiles = np.gcd.reduce([x for x in displacement.flat if x != 0])
    u = (1/number_of_tiles) * displacement
    return not (None in [find_hex(board, hex2.location + i*u) for i in range(number_of_tiles)])

def linked_hexes(board, starting_hex)
    #given a hex, return the list of all hexes which can be connected to the starting hex by a path of monochromatic auras
    

if __name__ == "__main__":
    boardfriend = Board('Dark')
    hexfriend = find_hex(boardfriend, np.matrix([0,0,0]))
    hexenemy = find_hex(boardfriend, np.matrix([52,0,1]))


    print(find_adjacent_hexes(boardfriend,hexfriend))
    print(leap_eligible(boardfriend, hexfriend, find_hex(boardfriend,[2,0,-2])))
