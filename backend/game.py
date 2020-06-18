"""
Overall game class to track info related to turns and the board.
"""
from backend.board import Board
from backend.errors import InvalidMove
from backend.helpers import other_faction
from backend.location import find_adjacent_hexes
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

        player = self.get_current_player()
        adj_hexes = find_adjacent_hexes(self.current_board, player.hex)
        adj_hexes_wo_objs = [h for h in adj_hexes if h.occupant == None]
        # TODO: make functions in location.py to do ^ filtering + its opposite

        if len(adj_hexes_wo_objs) == 0:
            raise InvalidMove('There is no adjacent hex for you to move')
        elif len(adj_hexes_wo_objs) == 1:
            hex = adj_hexes_wo_objs[0]
            print('Moving to {}'.format(hex))
        else:
            hex = user_input.choose_from_list(adj_hexes_wo_objs)
        
        self.current_board.actions -= 1
        self.move_object(player, from_hex=player.hex, to_hex=hex)

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
            player.hex.aura = self.current_board.faction
        else:
            if n_actions < 2:
                raise InvalidMove('You cannot bless because you have {} action{} remaining'.format(
                    n_actions,
                    '' if n_actions == 1 else 's',
                ))
            self.current_board.actions -= 2
            player.hex.aura = self.current_board.faction

    def drop(self):
        if self.current_board.actions < 1:
            raise InvalidMove('You cannot drop because you have no more actions')
        
        # get list of eligible hexes
        player = self.get_current_player()
        adj_hexes = find_adjacent_hexes(self.current_board, player.hex)
        adj_hexes_wo_objs = [h for h in adj_hexes if h.occupant == None]
        if len(adj_hexes_wo_objs) == 0:
            raise InvalidMove('There is no adjacent hex where you can drop')
        
        # get list of eligible artworks
        faction = self.current_board.faction
        eligible_artworks = []
        for artwork in self.current_board.artworks:
            if artwork.faction == faction and artwork.hex == None:
                eligible_artworks.append(artwork)
        if len(eligible_artworks) == 0:
            raise InvalidMove('{} does not have any unplaced artworks'.format(faction))

        # prompt for hex choice if needed
        if len(adj_hexes_wo_objs) == 1:
            hex = adj_hexes_wo_objs[0]
            print('Dropping on {}'.format(hex))
        else:
            hex = user_input.choose_from_list(adj_hexes_wo_objs)

        # prompt for artwork choice if needed
        if len(eligible_artworks) == 1:
            artwork = eligible_artworks[0]
            print('Dropping {}'.format(artwork))
        else:
            artwork = user_input.choose_from_list(eligible_artworks)
        
        self.current_board.actions -= 1
        self.move_object(artwork, to_hex=hex)

    def pick_up(self):
        if self.current_board.actions < 1:
            raise InvalidMove('You cannot pick up because you have no more actions')
        print('You want to pick up but that\'s not implemented yet... skipping')
        
        # get list of eligible hexes
        player = self.get_current_player()
        adj_hexes = find_adjacent_hexes(self.current_board, player.hex)
        
        # get list of eligible artworks
        faction = self.current_board.faction
        eligible_artworks = []
        for artwork in self.current_board.artworks:
            if artwork.faction == faction and artwork.hex in adj_hexes:
                eligible_artworks.append(artwork)
        if len(eligible_artworks) == 0:
            raise InvalidMove('{} does not have any adjacent artworks to pick up'.format(faction))

        # prompt for artwork choice if needed
        if len(eligible_artworks) == 1:
            artwork = eligible_artworks[0]
            print('Picking up {}'.format(artwork))
        else:
            artwork = user_input.choose_from_list(eligible_artworks)
        
        self.current_board.actions -= 1
        self.move_object(artwork, from_hex=artwork.hex)

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
        
        light_player = self.current_board.players['Light']
        dark_player = self.current_board.players['Dark']
        hex1 = self.current_board.rooms[0].hexes[0]
        hex2 = self.current_board.rooms[0].hexes[1]

        self.move_object(light_player, to_hex=hex1)
        self.move_object(dark_player, to_hex=hex2)

    def move_object(self, occupant, from_hex=None, to_hex=None):
        # order matters here, updating occupant.hex last make it ok for from_hex to be occupant.hex initially
        if from_hex != None:
            from_hex.occupant = None
        if to_hex != None:
            to_hex.occupant = occupant
        occupant.hex = to_hex

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
