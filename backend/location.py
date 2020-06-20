"""
A location is a vector of three integers whose entries sum to zero.
This is implemented using numpy's array class.
Location Servies: thank Apple for assisting surveillance
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
        for test_hex in room.hexes:
            if (test_hex.location == location).all():
                return test_hex
    return None

def find_neighbor_hex(board, starting_hex, direction):
    #find the hex at direction relative to direction
    return find_hex(board, starting_hex.location + direction)

def find_adjacent_hexes(board, starting_hex, return_nones = False):
    #given a hex, return the (up to six) neighboring hexes
    return [ item for item in  [find_neighbor_hex(board,starting_hex,u) for u in unit_directions] if (item != None or return_nones)]

def leap_eligible(board, hex1, hex2):
    if hex1 == hex2:
        return False
    #returns true if two pieces on hex1 and hex2 can Leap, and false otherwise
    try:
        displacement = hex1.location - hex2.location
    except AttributeError:
        print("You tried to leap, but passed nonexistent hexes or locations. Shame on you.")
        return False
    nonzero_entries = [x for x in displacement.flat if x != 0]
    number_of_tiles = np.gcd.reduce(nonzero_entries)
    u = (1/number_of_tiles) * displacement
    return not (None in [find_hex(board, hex2.location + i*u) for i in range(number_of_tiles)])

def linked_search(board, starting_hex, check_auras, check_boundary):
    # given a hex, return the list of all hexes connected to the starting hex
    # if check_auras, return the list of hexes connected to the starting hex by monochromatic auras
    # breadth-first search
    visited_hexes = [starting_hex]
    # a list of lists of hexes found at each step
    list_of_steps = [[starting_hex]]
    new_hex_list = []
    boundary = []
    while list_of_steps[-1] != []:
        for current_hex in list_of_steps[-1]:
            #iterate over hexes found in the last step
            for candidate_hex in find_adjacent_hexes(board, current_hex):
                #check if the current hex's neighbors are the same aura as the start
                if not(candidate_hex in visited_hexes):
                    # add the new hex to the list IF not checking auras OR IF it has the right aura
                    if (not check_auras) or (candidate_hex.aura == starting_hex.aura):
                        visited_hexes.append(candidate_hex)
                        new_hex_list.append(candidate_hex)
                    # if computing the boundary, add it to the boundary
                    elif check_boundary and not(candidate_hex in boundary):
                        boundary.append(candidate_hex)
        list_of_steps.append(deepcopy(new_hex_list))
        new_hex_list = []
    if check_boundary:
        return boundary
    else:
        return visited_hexes

def linked_hexes(board, starting_hex):
    # search for linked hexes, check if they are the same aura, and don't return the boundary
    return linked_search(board, starting_hex, True, False)

def adjacent_linked_region(board, starting_hex):
    # search for linked hexes, check if they are the same aura, and return the boundary
    return linked_search(board, starting_hex, True, True)

def linked_rooms(board, starting_hex):
    linked_hex = linked_hexes(board,starting_hex)
    linked_room = []
    for room in board.rooms:
        for test_hex in room.hexes:
            if test_hex in linked_hex:
                linked_room.append(room)
                break
    return linked_room

def neighboring_region(board, hex_list):
    neighbors = []
    for current_hex in hex_list:
        for test_hex in find_adjacent_hexes(board, current_hex):
            if not(test_hex in neighbors or test_hex in hex_list):
                neighbors.append(test_hex)
    return neighbors

"""
if __name__ == "__main__":
    from backend.board import Board

    board = Board('Dark')
    test_hex = find_hex(board, np.matrix([0,0,0]))
    test_hex.aura = 'Light'
    find_hex(board, np.matrix([1,0,-1])).aura = 'Light'
    find_hex(board, np.matrix([2,-3,1])).aura = 'Light'
    
    print([str(x) for x in linked_hexes(board,test_hex)])
    print([str(x) for x in adjacent_linked_region(board, test_hex)])
"""

