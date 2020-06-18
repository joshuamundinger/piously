"""
Overall game class to track info related to turns and the board.
"""
from backend.board import Board
from backend.errors import InvalidMove
from backend.helpers import other_faction
from backend.operation import Operation
import backend.user_input as user_input
import copy

class Game(object):
    def __init__(self, start_faction):
        self.old_board = Board(start_faction)
        self.current_board = copy.deepcopy(self.old_board)

    def __str__(self):
        return str(self.current_board)

    def is_game_over(self):
        pass

    def get_current_player(self):
        return self.current_board.get_current_player()

    def move(self):
        if self.current_board.actions < 1:
            raise InvalidMove('You cannot move because you have no more actions')

        print('You want to move but that\'s not implemented yet... skipping')
        self.current_board.actions -= 1

    def bless(self):
        player = self.get_current_player()
        old_aura = player.hex.aura
        n_actions = self.current_board.actions

        if old_aura == self.current_board.faction:
            raise InvalidMove('You cannot bless a hex that already has your aura')
        elif old_aura == None:
            if n_actions < 1:
                raise InvalidMove('You cannot bless because you have no more actions')
            self.current_board.actions -= 1
            Operation(player.hex, self.current_board.faction).apply(self.current_board)
        else:
            if n_actions < 2:
                raise InvalidMove('You cannot bless because you have {} action{} remaining'.format(
                    n_actions,
                    '' if n_actions == 1 else 's',
                ))
            self.current_board.actions -= 2
            Operation(player.hex, self.current_board.faction).apply(self.current_board)

    def drop(self):
        if self.current_board.actions < 1:
            raise InvalidMove('You cannot drop because you have no more actions')
        print('You want to drop but that\'s not implemented yet... skipping')
        self.current_board.actions -= 1

    def pick_up(self):
        if self.current_board.actions < 1:
            raise InvalidMove('You cannot pick up because you have no more actions')
        print('You want to pick up but that\'s not implemented yet... skipping')
        self.current_board.actions -= 1

    def cast_spell(self):
        spell = user_input.choose_spell(self.current_board)

        # TODO: need to prompt for any needed input and properly fill in operations
        # or could implement this on each spell individually
        operations = []
        spell.cast(self.current_board, operations) 

    def reset_turn(self):
        self.current_board = copy.deepcopy(self.old_board)

    def maybe_claim_spell(self):
        a_spell = self.get_current_player().hex.room.artwork
        if a_spell.faction == None:
            b_spell = self.get_current_player().hex.room.bewitchment
            chosen_spell = user_input.choose_spell_to_take(a_spell, b_spell)

            if chosen_spell != None:
                a_spell.faction = other_faction(self.current_board.faction)
                b_spell.faction = other_faction(self.current_board.faction)
                chosen_spell.faction = self.current_board.faction
                a_spell.artwork.faction = a_spell.faction
        else:
            print('Spells for current room are already claimed')

    def end_turn(self):
        if self.current_board.actions < 0:
            raise InvalidMove('You cannot end turn with negative actions, please reset turn and try again')
        self.maybe_claim_spell()

        print('ENDING TURN')
        self.current_board.end_turn()
        self.old_board = copy.deepcopy(self.current_board)

    def sync_boards(self):
        self.old_board = copy.deepcopy(self.current_board)

    def place_rooms(self):
        print('choosing room postitons is not implented yet... initializing positions')
        # TODO: at least hard code a starting board
        pass

    def place_players(self):
        print('choosing player starting postiton is not implented yet... initializing positions')
        
        operations = [
            Operation('1', 'p', {'occupant': 'd'}), # place dark player on hex 1
            Operation('2', 'p', {'occupant': 'l'}), # place light player on hex 2
        ]

        [operation.apply(self.current_board) for operation in operations]

if __name__ == "__main__":
    piously = Game("Dark")
    
    # set up board
    piously.place_rooms()
    piously.place_players()
    piously.sync_boards() # needed so that restart_turn works correctly on the first turn

    # enter main game loop
    while not piously.is_game_over():
        print(piously)
        move_type = user_input.choose_move(piously.current_board)
        try: 
            if move_type == 'move':
                piously.move()
            elif move_type == 'bless':
                piously.bless()
            elif move_type == 'drop':
                piously.drop()
            elif move_type == 'pick up':
                piously.pick_up()
            elif move_type == 'cast spell':
                piously.cast_spell()
            elif move_type == 'end turn':
                piously.end_turn()
            elif move_type == 'reset turn':
                piously.reset_turn()
            elif move_type == 'end':
                current_faction = piously.current_board.faction
                print('{} forefits, {} wins!'.format(current_faction, other_faction(current_faction)))
                break
        except InvalidMove as move:
            input('{} '.format(move))
    
    print('Goodbye :)\n')
