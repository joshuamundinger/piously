"""
A location is a vector of three integers whose entries sum to zero.
This is implemented using numpy's array class.

This file has lots of different helpers for working with locations and
computing linked regions
"""
import numpy as np

unit_directions = [
    np.matrix([1,0,-1]),
    np.matrix([-1,1,0]),
    np.matrix([0,-1,1]),
    np.matrix([-1,0,1]),
    np.matrix([1,-1,0]),
    np.matrix([0,1,-1]),
]

# convert a location vector to a axial coordinate tuple
def location_to_axial(location):
    return (location.flat[0], location.flat[1])

# convert an axial coordinate tuple to a location vector
def axial_to_location(axial_pos):
    x, y = axial_pos
    return np.matrix([x, y, -1*x - y])

# return whether two hexes have the same location
def hexes_colocated(hex1, hex2):
    return not any([hex1.location.flat[i] - hex2.location.flat[i] for i in range(3)])

# given a board and a location, return the hex at this location, or None if no hex exists
def find_hex(board, location):
    for test_hex in board.get_all_hexes():
        if (test_hex.location == location).all():
            return test_hex
    return None

# find the hex at direction relative to direction
def find_neighbor_hex(board, starting_hex, direction):
    return find_hex(board, starting_hex.location + direction)

# given a hex, return the (up to six) neighboring hexes
def find_adjacent_hexes(board, starting_hex, return_nones = False):
    adjacent_hexes = []
    for u in unit_directions:
        neighbor = find_neighbor_hex(board, starting_hex, u)
        if neighbor != None or return_nones:
            adjacent_hexes.append(neighbor)
    return adjacent_hexes

# return True if two pieces on hex1 and hex2 can Leap, and False otherwise
def leap_eligible(board, hex1, hex2):
    if hex1 == hex2:
        return False
    try:
        displacement = hex1.location - hex2.location
    except AttributeError:
        # You tried to leap, but passed nonexistent hexes or locations. Shame on you.
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

# given a hex, return the list of all hexes connected to the starting hex
# if check_auras, only return hexes connected to the starting hex by monochromatic auras
# implements a breadth-first search
def linked_search(board, starting_hex, check_auras=True, return_boundary=False):
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
                    elif return_boundary and not(candidate_hex in boundary):
                        boundary.append(candidate_hex)
        list_of_steps.append(new_hex_list)
        new_hex_list = []

    if return_boundary:
        return boundary
    else:
        return visited_hexes

# search for linked hexes, check if they are the same aura, and don't return the boundary
def linked_hexes(board, starting_hex):
    return linked_search(board, starting_hex)

# search for linked hexes, check if they are the same aura, and return the boundary
def adjacent_linked_region(board, starting_hex):
    return linked_search(board, starting_hex, return_boundary=True)

def linked_rooms(board, starting_hex, include_shovel=True):
    linked_hex = linked_hexes(board, starting_hex)
    linked_room = []
    for room in board.rooms:
        for test_hex in room.hexes:
            if test_hex in linked_hex:
                if include_shovel or room.name != 'Shovel':
                    linked_room.append(room)
                    break
    return linked_room

# given hex_list, returns the list of all hexes adjacent to an element of
# hex_list, but not in hex_list
def neighboring_region(board, hex_list):
    neighbors = []
    for current_hex in hex_list:
        for test_hex in find_adjacent_hexes(board, current_hex):
            if not(test_hex in neighbors or test_hex in hex_list):
                neighbors.append(test_hex)
    return neighbors

# given a hex, find its room
def find_room(board, hex):
    return [room for room in board.rooms if hex in room.hexes][0]

def find_adjacent_rooms(board, starting_room, include_shovel=True):
    adjacent_rooms = []
    for hex in starting_room.hexes:
        # find the rooms which are next to hex
        for room in [find_room(board, test_hex) for test_hex in find_adjacent_hexes(board, hex)]:
            if not( room == starting_room or room in adjacent_rooms):
                if include_shovel or room.name != 'Shovel':
                    adjacent_rooms.append(room)
    return adjacent_rooms

# return locations adjacent to entries of hex_list which do not have hexes
def find_unoccupied_neighbors(board, hex_list):
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
