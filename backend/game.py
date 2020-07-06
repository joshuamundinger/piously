"""
Overall game class to track info related to turns and the board.
"""
from backend.board import Board
from backend.errors import InvalidMove
from backend.helpers import other_faction
from backend.location import find_adjacent_hexes, location_to_axial, linked_rooms
from graphics.pygame_screen import PygameScreen
from graphics.js_screen import MockScreen
import graphics.pygame_input as pygame_input
import graphics.js_input as js_input
import copy

# TODO:
# - cancel options - ex. when choosing spell to cast
# - audit use of raise InvalidMove vs setting error msg directly
# - consider refactoring so that current_action is lower level - ex click spell, click hex ect

class Game(object):
    def __init__(self, start_faction):
        # choose pygame vs js frontend
        # IMPORTANT: if you update, also update imports in spell.py
        self.mode = 'js' # 'js' or 'pygame'

        self.screen_input = js_input if self.mode == 'js' else pygame_input
        self.screen = MockScreen() if self.mode == 'js' else PygameScreen()
        self.old_board = Board(self.screen, start_faction)
        self.current_board = copy.deepcopy(self.old_board)
        self.game_over = False
        self.start_action = 'place rooms'

    def __str__(self):
        return str(self.current_board)

    def is_game_over(self):
        # for each aura'd hex in a room, check if the linked region has all seven rooms.
        winners = []
        for hex in self.current_board.rooms[0].hexes:
            if hex.aura:
                linked_names = [x.name for x in linked_rooms(self.current_board, hex)]
                if sorted(linked_names) == sorted(['P','I','O','U','S','L','Y']):
                    winners.append(hex.aura)
        win_set = set(winners)
        if not win_set:
            return None
        elif len(win_set) == 1:
            return winners[0]
        else:
            return "Tie"

    def get_current_player(self):
        return self.current_board.get_current_player()

    def move(self):
        if self.current_board.actions < 1:
            raise InvalidMove('You cannot move because you have no more actions')

        player = self.get_current_player()
        adj_hexes = find_adjacent_hexes(self.current_board, player.hex)
        adj_hexes_wo_objs = [h for h in adj_hexes if h.occupant == None]

        hex = self.screen_input.choose_hexes(
            self.screen,
            adj_hexes_wo_objs,
            'Click hex to move to',
            'There is no adjacent hex for you to move',
        )
        if hex == None:
            return False

        self.current_board.actions -= 1
        self.current_board.move_object(player, from_hex=player.hex, to_hex=hex)
        return True

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
        return True

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

        # prompt for artwork choice if needed
        artwork = self.screen.choice(0) or self.screen_input.choose_from_list(
            self.screen,
            eligible_artworks,
            'Choose artwork to drop:',
            '{} does not have any unplaced artworks'.format(faction)
        )
        if artwork == None:
            return False

        # prompt for hex choice if needed
        hex = self.screen_input.choose_hexes(
            self.screen,
            adj_hexes_wo_objs,
            'Click where to drop {}'.format(artwork),
            'There is no adjacent hex where you can drop',
        )
        if hex == None:
            return False

        self.current_board.actions -= 1
        self.current_board.move_object(artwork, to_hex=hex)
        return True

    def pick_up(self):
        if self.current_board.actions < 1:
            raise InvalidMove('You cannot pick up because you have no more actions')

        # get list of eligible hexes
        player = self.get_current_player()
        adj_hexes = find_adjacent_hexes(self.current_board, player.hex)

        # get list of eligible artworks
        faction = self.current_board.faction
        eligible_artworks = []
        coords = [] # coordinates of eligible_artworks
        for artwork in self.current_board.artworks:
            if artwork.faction == faction and artwork.hex in adj_hexes:
                eligible_artworks.append(artwork)
                coords.append(artwork.hex)

        # prompt for artwork choice if needed
        artwork_idx = self.screen_input.choose_hexes(
            self.screen,
            coords,
            'Click artwork to pick up',
            '{} does not have any adjacent artworks to pick up'.format(faction),
            return_index = True,
        )
        if artwork_idx == None:
            return False

        artwork = eligible_artworks[artwork_idx]

        self.current_board.actions -= 1
        self.current_board.move_object(artwork, from_hex=artwork.hex)
        return True

    def cast_spell(self):
        faction = self.current_board.faction
        eligible_spells = []
        for spell in self.current_board.spells:
            if spell.faction == faction:
                if not spell.tapped:
                    eligible_spells.append(spell)

        spell = self.screen.choice(0) or self.screen_input.choose_from_list(
            self.screen,
            eligible_spells,
            'Choose spell to cast:',
            '{} does not have untapped spells'.format(faction),
            all_spells = self.current_board.spells)
        if spell == None:
            return False

        return spell.cast(self.current_board)

    def reset_turn(self):
        self.current_board = copy.deepcopy(self.old_board)
        return True

    def maybe_claim_spell(self):
        a_spell = self.get_current_player().hex.room.artwork
        if a_spell.faction == None:
            b_spell = self.get_current_player().hex.room.bewitchment

            spells = [a_spell, b_spell, 'Neither']
            chosen_spell = self.screen_input.choose_from_list(
                self.screen,
                spells,
                'Choose spell to claim:'
            )
            if chosen_spell == None:
                return False

            print('chosen spell {}'.format(chosen_spell))
            if chosen_spell != 'Neither':
                a_spell.faction = other_faction(self.current_board.faction)
                b_spell.faction = other_faction(self.current_board.faction)
                chosen_spell.faction = self.current_board.faction
                a_spell.artwork.faction = a_spell.faction

        return True

    def end_turn(self):
        if self.current_board.actions < 0:
            raise InvalidMove('You cannot end turn with negative actions, please reset turn and try again')

        if self.maybe_claim_spell():
            self.current_board.end_turn()
            self.old_board = copy.deepcopy(self.current_board)
            return True
        else:
            return False

    def sync_boards(self):
        self.old_board = copy.deepcopy(self.current_board)

    def place_rooms(self):
        instructions = "Arrow keys to move | , . to rotate | l to toggle | enter to end."

        if len(self.screen.choices) == 0:
            self.screen.choices.append(None)

        # keep track of current room
        current_room = self.screen.choice(0) or self.current_board.rooms[0]
        current_room_index = self.current_board.rooms.index(current_room)

        # if this is the first call to place_rooms, set welcome message
        if not self.screen.choice(0):
            self.current_board.screen.info.text = "{}\nMoving room {}. {}".format(
                'Welcome to Piously! Dark begins by arranging the board.',
                current_room.name,
                instructions,
            )

        setting_up_board = True
        while setting_up_board:
            self.current_board.flush_hex_data()
            key = self.screen_input.get_keypress(self.current_board.screen)
            if key == None:
                return False
            elif key == "l":
                print('checking toggle (l)')
                if self.current_board.check_for_collisions(current_room):
                    self.current_board.screen.info.error = "Avoid collisions!"
                else:
                    current_room_index = ((current_room_index + 1) % 7)
                    current_room = self.current_board.rooms[current_room_index]
                    self.screen.choices[0] = current_room
                    self.current_board.screen.info.text = \
                        "Moving room {}.\n{}".format(current_room.name, instructions)
            elif key == "return" or key == "Enter":
                print('checking end board setup')
                # check to see if board satisfies connectivity rules
                if self.current_board.check_for_collisions(current_room):
                    self.current_board.screen.info.error = "Avoid collisions!"
                else:
                    setting_up_board = not(self.current_board.connectivity_test())
                    if setting_up_board:
                        self.current_board.screen.info.error = "Board not connected."
            else:
                current_room.keyboard_movement(key)
                self.current_board.screen.info.error = None

        self.current_board.screen.info.error = None
        return True

    def place_players(self):
        # TODO: let light pick who places first
        light_player = self.current_board.players['Light']
        dark_player = self.current_board.players['Dark']
        player_spots = self.current_board.get_all_hexes()

        if not self.screen.choice(0):
            hex2 = self.screen_input.choose_hexes(
                self.current_board.screen,
                player_spots,
                prompt_text = "Click to place the Dark player"
            )
            if hex2 == None:
                return False
            self.current_board.move_object(dark_player, to_hex=hex2)
            self.current_board.flush_player_data()
        player_spots.remove(self.screen.choice(0) or hex2)

        hex1 = self.screen_input.choose_hexes(
            self.current_board.screen,
            player_spots,
            prompt_text = "Now click to place the Light player"
        )
        if hex1 == None:
            return False
        self.current_board.move_object(light_player, to_hex=hex1)
        self.current_board.flush_player_data()
        return True

    # main method for pygame frontend
    def play(self):
        # set up board
        self.place_rooms()
        self.place_players()
        self.sync_boards() # needed so that restart_turn works correctly on the first turn

        # enter main game loop
        while not self.is_game_over():
            self.current_board.flush_gamepieces()
            move_type = self.screen_input.choose_move(self.screen)
            self.screen.info.error = None
            try:
                if move_type == 'move':
                    self.move()
                elif move_type == 'bless':
                    self.bless()
                elif move_type == 'drop':
                    self.drop()
                elif move_type == 'pick up':
                    self.pick_up()
                elif move_type == 'cast spell':
                    self.cast_spell()
                elif move_type == 'end turn':
                    self.end_turn()
                elif move_type == 'reset turn':
                    self.reset_turn()
                elif move_type == 'end game':
                    confirmation = self.screen_input.choose_from_list(
                        self.screen,
                        ['Yes', 'No'],
                        'Are you sure you want to forfeit and quit?'
                    )
                    if confirmation == 'Yes':
                        break
            except InvalidMove as move:
                self.screen.info.error = '{} '.format(move)
        self.end_game()
        self.screen.info.error = "Click on any hex to exit"
        self.screen_input.get_click(self.screen)

    def end_game(self):
        self.game_over = True
        winning_faction = self.is_game_over()
        if winning_faction:
            self.screen.info.text = "WINNER: {}".format(winning_faction)
        else:
            current_faction = self.current_board.faction
            self.screen.info.text = '{} forefits, {} wins!'.format(
                current_faction,
                other_faction(current_faction),
            )
        return True


    def do_action_helper(self, move_type):
        done = False
        verb = ''

        if move_type == 'move':
            done = self.move()
            verb = 'Done moving'
        elif move_type == 'bless':
            done = self.bless()
            verb = 'Done blessing'
        elif move_type == 'drop':
            done = self.drop()
            verb = 'Done dropping'
        elif move_type == 'pick up':
            done = self.pick_up()
            verb = 'Done picking up'
        elif move_type == 'cast spell':
            done = self.cast_spell()
            verb = 'Done casting'
        elif move_type == 'end turn':
            done = self.end_turn()
            verb = 'Turn ended'
        elif move_type == 'reset turn':
            done = self.reset_turn()
            verb = 'Turn reset'
        elif move_type == 'end game':
            # TODO: get confirmation
            done = self.end_game()
            verb = 'Game over'
        elif move_type == 'place rooms':
            done = self.place_rooms()
            verb = 'Board setup done'
        elif move_type == 'place players':
            done = self.place_players()
            verb = 'Player setup done'
        elif move_type == 'none':
            # This happens if the page is refreshed
            pass

            # self.screen.info.text = \
            #     'Welcome to Piously! Press arrow keys to arrange board'
            # self.screen.info.error = 'Implementation in progress'

        print('move:{} done:{} buttons_on:{}'.format(
            move_type, done, self.screen.action_buttons_on
        ))
        return done, verb

    # main method for js frontend
    def do_action(self, data):
        select_option_text = 'Select an option (click button or use keybinding)'
        if self.is_game_over():
            self.end_game()
        else:
            self.screen.data = data
            move_type = data['current_action']
            self.screen.info.error = None

            try:
                done, verb = self.do_action_helper(move_type)

                if done:
                    self.screen.choices = []
                    if move_type == 'place rooms':
                        self.sync_boards()
                        self.screen.action_buttons_on = False
                        self.screen.info.text = '{}. {}'.format(verb, 'Click to place Dark player')
                        self.start_action = 'place players'
                        data['current_action'] = 'place players'
                    elif move_type == 'place players':
                        self.sync_boards()
                        self.screen.action_buttons_on = True # TODO: redundant??

                        # TODO: don't hard code who goes first
                        self.screen.info.text = '{}! Dark goes first.\n{}'.format(verb, select_option_text)
                        self.start_action = 'none'
                        data['current_action'] = 'none'
                    else:
                        self.screen.action_buttons_on = True # TODO: redundant??
                        self.screen.info.text = '{}. {}'.format(verb, select_option_text)
                        data['current_action'] = 'none'

            except InvalidMove as error:
                self.screen.info.text = select_option_text
                self.screen.info.error = str(error)
                self.screen.choices = []
                self.screen.action_buttons_on = True
                data['current_action'] = 'none'

        print('setting state')
        state = {
            'info': self.screen.info.text,
            'error': self.screen.info.error,
            'action_buttons_on': self.screen.action_buttons_on,
            'current_player': self.current_board.faction,
            'current_action': data['current_action'],
            'actions': self.current_board.actions,
            'hexes': self.current_board.return_hex_data(),
            'players': self.current_board.return_player_data(),
            'spells': self.current_board.return_spell_data(),
            'game_over': self.game_over,
        }
        return state


if __name__ == "__main__":
    piously = Game("Dark")
    piously.play()
