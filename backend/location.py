"""
A location is a vector of three integers whose entries sum to zero.
This is implemented using numpy's array class.
Location Servies: thank Apple for assisting surveillance
"""

import numpy as np
from backend.errors import InvalidMove
from backend.hex import Hex
from copy import deepcopy

def location_to_axial(location):
    return (location.flat[0], location.flat[1])

def axial_to_location(axial_pos):
    x, y = axial_pos
    return np.matrix([x, y, -1*x - y])

unit_directions = [
        np.matrix([1,0,-1]),
        np.matrix([-1,1,0]),
        np.matrix([0,-1,1]),
        np.matrix([-1,0,1]),
        np.matrix([1,-1,0]),
        np.matrix([0,1,-1])
    ]

def hexes_colocated(hex1, hex2):
    # returns whether two hexes have the same location
    return not any([hex1.location.flat[i] - hex2.location.flat[i] for i in range(3)])

def find_hex(board, location):
    # given a board and a location, return the hex at this location, or None if no hex exists
    for room in board.rooms:
        for test_hex in room.hexes:
            if (test_hex.location == location).all():
                return test_hex
    return None

def find_hex_axial(board, axial_pos):
    return find_hex(board, axial_to_location(axial_pos))

def find_neighbor_hex(board, starting_hex, direction):
    # find the hex at direction relative to direction
    return find_hex(board, starting_hex.location + direction)

def find_adjacent_hexes(board, starting_hex, return_nones = False):
    # given a hex, return the (up to six) neighboring hexes
    return [ item for item in  [find_neighbor_hex(board,starting_hex,u) for u in unit_directions] if (item != None or return_nones)]

def leap_eligible(board, hex1, hex2):
    if hex1 == hex2:
        return False
    # returns True if two pieces on hex1 and hex2 can Leap, and False otherwise
    try:
        displacement = hex1.location - hex2.location
    except AttributeError:
        print("You tried to leap, but passed nonexistent hexes or locations. Shame on you.")
        return False
    nonzero_entries = [x for x in displacement.flat if x != 0]
    number_of_tiles = np.gcd.reduce(nonzero_entries)
    # get a "unit" vector in the direction between hex1 and hex2
    u = (1/number_of_tiles) * displacement
    # check to see if the pieces are aligned along one of the three coordinate lines,
    # which is equivalent to if u-x is zero for x in unit_directions
    if all([ (u-x).any() for x in unit_directions]):
        return False
    else:
        # check each position in the row and make sure none are empty
        for i in range(number_of_tiles):
            if not find_hex(board, hex2.location + i*u):
                return False
        return True

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
        # iterate over hexes found in the last step
        for current_hex in list_of_steps[-1]:
            for candidate_hex in find_adjacent_hexes(board, current_hex):
                # check if the current hex's neighbors have not been visited
                # below code is to handle if two different pointers to the same object are passed
                if all([ not(hexes_colocated(x, candidate_hex)) for x in visited_hexes]):
                    # add the new hex to the list IF not checking auras OR IF it has the right aura
                    if (not check_auras) or (candidate_hex.aura == starting_hex.aura):
                        visited_hexes.append(candidate_hex)
                        new_hex_list.append(candidate_hex)
                    # if computing the boundary, add it to the boundary
                    elif check_boundary and not(candidate_hex in boundary):
                        boundary.append(candidate_hex)
        # TODO: dont think deepcopy is needed -> try removing
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
    # given hex_list, returns the list of all hexes adjacent to an element of hex_list,
    # but not in hex_list
    neighbors = []
    for current_hex in hex_list:
        for test_hex in find_adjacent_hexes(board, current_hex):
            if not(test_hex in neighbors or test_hex in hex_list):
                neighbors.append(test_hex)
    return neighbors

# given a hex, find its room
def find_room(board, hex):
    return [room for room in board.rooms if hex in room.hexes][0]

def find_adjacent_rooms(board, starting_room):
    adjacent_rooms = []
    for hex in starting_room.hexes:
        for room in [find_room(board, test_hex) for test_hex in find_adjacent_hexes(board, hex)]:
            if not( room == starting_room or room in adjacent_rooms):
                adjacent_rooms.append(room)
    return adjacent_rooms

def find_unoccupied_neighbors(board, hex_list):
    # return locations adjacent to entries of hex_list which do not have hexes
    unoccupied_locations = []
    for hex in hex_list:
        for u in unit_directions:
            # see if there is a hex in direction u from hex
            test_location = hex.location + u
            if not(find_neighbor_hex(board,hex,u)):
                unoccupied_locations.append(test_location)
    # TODO: remove duplicates from unoccupied_locations
    # it cannot be cast to set since matrices are not hashable
    return unoccupied_locations
