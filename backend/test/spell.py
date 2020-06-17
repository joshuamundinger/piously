from backend.board import Board
from backend.operation import Operation

def test_opportunist():
    # opportunist = q
    print('opportunist')

    # SETUP
    # get board and two spells
    board = Board("Light")
    opportunist = board.str_to_spell('q')
    to_untap = board.str_to_spell('w')
    assert(opportunist.tapped == False)
    assert(to_untap.tapped == False)
    
    # init values for test
    opportunist.faction = "Light"
    to_untap.faction = "Light"
    to_untap.toggle_tapped() 
    assert(opportunist.tapped == False)
    assert(to_untap.tapped == True)
    
    # TEST
    # casting opportunist should untap the indicated spell and tap opportunist
    opportunist.cast(board, 'w')
    assert(opportunist.tapped == True)
    assert(to_untap.tapped == False)

    # _validate_operations
    # operations = [Operation('n', 'u', {'spell': 'w'})]
    # opportunist._validate_operations(board, operations)
