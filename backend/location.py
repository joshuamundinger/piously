"""
A location is a vector of three integers whose entries sum to zero.
This is implemented using numpy's array class
"""

import numpy as np
from backend.board import Board
#from backend.hex import Hex

def find_hex(board, location):
    #given a board and a location, return the hex at this location, or None if no hex exists
    for room in board.rooms:
        for hexa in room.hexes:
            if (hexa.location == location).all():
                return hexa
    return None




if __name__ == "__main__":
    boardfriend = Board('Dark')
    hexfriend = find_hex(boardfriend, np.matrix([1,0,-1]))
    hexenemy = find_hex(boardfriend, np.matrix([52,0,1]))
    print hexfriend, hexenemy

