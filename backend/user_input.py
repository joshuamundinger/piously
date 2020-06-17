"""
User input helper functions. Currently they all rely on keypresses, but eventaully they will be based on clicks on the UI.
Some of them are just to make testing easu
"""

from backend.operation import Operation 

def choose_move(board):
    '''
    Params: none
    Returns: string representation of the move to make
    '''
    while True:
        move_type = input('> Would you like to (1) move (2) bless (3) drop (4) pick up (5) cast spell (6) end turn or (7) restart turn? ')

        if move_type == '1':
            return 'move'
        elif move_type == '2':
            return 'bless'
        elif move_type == '3':
            return 'drop'
        elif move_type == '4':
            return 'pick up'
        elif move_type == '5':
            return 'cast spell'
        elif move_type == '6':
            return 'end turn'
        elif move_type == '7':
            return 'reset turn'
        elif move_type == "'": # when this is removed, also remove board param and operation import
            choose_and_apply_cheat(board)
        else:
            print('Please enter a number 1-7')

def choose_and_apply_cheat(board):
    print('Enter any operation')
    h = choose_hex(board)
    change, extra = choose_change(board)
    Operation(h, change, extra).apply(board)
    print(board)

'''
Params: Board object to get hexes from
Returns: chosen Hex object
'''
def choose_hex(board):
    while True:
        hex_str = input('> What hex do you want? ')
        try:
            return board.str_to_hex(hex_str)
        except NameError:
            print('Please enter one of [1234 5678 qwer tyui asdf ghjk zxcv b n]')

'''
Params: Board object to get changes from
Returns: chosen Hex object
'''
def choose_change(board):
    while True:
        change_str = input('> What change do you want? ')

        if change_str in ['l', 'd', 'n', 'a', 's']:
            return change_str, {}
        elif change_str == 'm':
            return change_str, {'location': choose_location(board)}
        elif change_str in ['p', 'r']:
            return change_str, {'occupant': choose_occupant(board)}
        elif change_str in ['u', 'c']:
            return change_str, {'spell': choose_spell(board)}
        else:
            print('Please enter one of l/d/n (to update aura), a/s (to update # actions), p/r (act on object), u/c (act on spell)')

def choose_location(board):
    print('choose location not implemented')
    return None # TODO

'''
Params: Board object to get spell from
Returns: chosen Spell object
'''
def choose_spell(board):
    while True:
        spell_str = input('> What spell do you want? ')
        try:
            return board.str_to_spell(spell_str)
        except NameError:
            print('Please enter one of [12 56 qw ty as gh zx] (in each pair first one is artwork, second is bewitchment)')

'''
Params: Board object to get artworks + players from
Returns: chosen Artwork / Player object
'''
def choose_occupant(board):
    while True:
        spell_str = input('> What occupant do you want? ')
        try:
            return board.str_to_occupant(spell_str)
        except NameError:
            print('Please enter one of [1 5 q t a g z d l]')

'''
This is useful for moves like pick_up and purify where the valid objects are adjacent to the given hex
'''
# def choose_adjacent_occupant(board):
#     hex = board.get_current_player().hex
#     adjacent_hexes = board.get_adjacent_hexes(hex)
#     adjacent_occupants = adjacent_hexes.fil
#     print('> Choose an object')
#     for idx, h in enumerate(adjacent_hexes):
#         print(' ({}) {}'.format(idx + 1, h))

def choose_spell_to_take(a_spell, b_spell):
    while True:
        spell_str = input('> Would you like to take a spell? Enter (1) for {}, (2) for {}, or (3) for No '.format(a_spell.name, b_spell.name))
        if spell_str == '1':
            return a_spell
        elif spell_str == '2':
            return b_spell
        else:
            print('Please enter a number 1-3')
