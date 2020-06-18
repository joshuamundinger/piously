"""
A location is a vector of three integers whose entries sum to zero.
This is implemented using numpy's array class
"""

import numpy as np
from backend.errors import InvalidMove
from backend.hex import Hex
from copy import deepcopy

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

def linked_hexes(board, starting_hex):
    #given a hex, return the list of all hexes which can be connected to the starting hex by a path of monochromatic auras
    #breadth-first search
    visited_hexes = [starting_hex]
    #a list of lists of hexes found at each step
    list_of_steps = [[starting_hex]]
    new_hex_list = []
    while list_of_steps[-1] != []:
        for current_hex in list_of_steps[-1]:
            #iterate over hexes found in the last step
            for candidate_hex in find_adjacent_hexes(board, current_hex):
                #check if the current hex's neighbors are the same aura as the start
                if not(candidate_hex in visited_hexes) and (candidate_hex.aura == starting_hex.aura):
                    visited_hexes.append(candidate_hex)
                    new_hex_list.append(candidate_hex)
        list_of_steps.append(deepcopy(new_hex_list))
        new_hex_list = []
    return visited_hexes

def adjacent_linked_region(board, starting_hex):
    linked = linked_hexes(board, starting_hex)
    neighbors = []
    #this is a pretty wasteful implementation
    for current_hex in linked:
        for candidate_hex in find_adjacent_hexes(board, current_hex):
            if not(candidate_hex in linked):
                neighbors.append(candidate_hex)
    return neighbors




if __name__ == "__main__":
    from backend.board import Board

    board = Board('Dark')
    test_hex = find_hex(board, np.matrix([0,0,0]))
    test_hex.aura = 'Light'
    find_hex(board, np.matrix([1,0,-1])).aura = 'Light'
    find_hex(board, np.matrix([2,-3,1])).aura = 'Light'

    print(linked_hexes(board,test_hex))

