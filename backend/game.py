"""
Overall game class to track info related to turns and the board.
"""
from backend.board import Board
from backend.errors import InvalidMove
from backend.helpers import other_faction
from backend.location import find_adjacent_hexes, location_to_axial
from graphics.pygame_screen import PygameScreen
from graphics.js_screen import MockScreen
import graphics.pygame_input as pygame_input
import graphics.js_input as js_input
import copy
from json import dump
from datetime import datetime as dt

# TODO:
# - cancel options - ex. when choosing spell to cast
# - audit use of raise InvalidMove vs setting error msg directly
# - consider refactoring so that current_action is lower level - ex click spell, click hex ect
# - remove start_faction param from Game
# - make database or logging to
#    - track # games played
#    - track who started, who won, and with what spells
#    - not loose game state when server restarts

class Game(object):
    def __init__(self, game_id):
        # choose pygame vs js frontend
        # IMPORTANT: if you update, also update imports in spell.py
        self.mode = 'js' # 'js' or 'pygame'

        self.game_id = game_id
        self.screen_input = js_input if self.mode == 'js' else pygame_input
        self.screen = MockScreen() if self.mode == 'js' else PygameScreen()
        self.old_board = Board(self.screen)
        self.current_board = copy.deepcopy(self.old_board)
        self.start_action = 'place rooms'

        self.created = Game.current_time_str()
        self.updated = Game.current_time_str()

    def __str__(self):
        return str(self.current_board)

    def is_game_over(self):
        return self.current_board.is_game_over()

    def get_current_player(self):
        return self.current_board.get_current_player()

    @staticmethod
    def from_hash(hash):
        game = Game(hash['game_id'])
        hash['screen'] = game.screen

        # TODO: make it work to save games that are still in setup steps
        # This would require saving start action and moving screen.choices to use indices.
        game.start_action = hash['start_action'] if 'start_action' in hash else 'none'
        game.created = hash['created']
        game.updated = hash['updated']

        board = Board.from_hash(hash)
        game.current_board = board
        game.sync_boards()

        return game

    @staticmethod
    def filename(game_id=None):
        if game_id:
            return 'saved_games/{}.json'.format(game_id)
        else:
            return 'saved_games'

    @staticmethod
    def current_time_str():
        return dt.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    def save_to_file(self):
        data = self.get_game_state(include_metadata=True)
        with open(Game.filename(self.game_id), "w") as file:
            dump(data, file)

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

        artwork = self.screen.choice(0)
        if artwork == None:
            # set artwork based on click if it's been chosen
            if 'click_spell_idx' in self.screen.data:
                spell_idx = self.screen.data['click_spell_idx']
                click_artwork = self.current_board.spells[spell_idx].artwork
                self.screen.data.pop('click_spell_idx')
                if click_artwork in eligible_artworks:
                     artwork = click_artwork
                     self.screen.choices.append(artwork)

            # otherwise, get user input
            else:
                artwork = self.screen_input.choose_from_list(
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
        eligible_spells = self.current_board.get_eligible_spells()

        # TODO[idea]: consider also allowing clicking on artwork to choose spell
        spell = self.screen.choice(0) or self.screen_input.choose_from_list(
            self.screen,
            eligible_spells,
            'Choose spell to cast:',
            '{} does any spells that can be cast'.format(self.current_board.faction),
            all_spells = self.current_board.spells)
        if spell == None:
            return False

        try:
            done = spell.cast(self.current_board)
        except InvalidMove as error:
            spell.untap() # mark spell untapped since it did not complete
            raise InvalidMove(str(error))
            # TODO: make sure no spells raise after mutating game state
            # TODO[idea]: store a 3rd version of board to reset action and use
            # that here

        return done

    def reset_turn(self):
        self.current_board = copy.deepcopy(self.old_board)
        return True

    def maybe_claim_spell(self):
        a_spell = self.get_current_player().hex.room.artwork
        if a_spell and a_spell.faction == None:
            b_spell = self.get_current_player().hex.room.bewitchment

            spells = [a_spell, b_spell, 'Neither']
            chosen_spell = self.screen_input.choose_from_list(
                self.screen,
                spells,
                'Choose spell to claim:'
            )
            if chosen_spell == None:
                return False

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
            self.current_board.end_turn() # update faction, untap spells, reset # actions
            self.sync_boards()
            return True
        else:
            return False

    def sync_boards(self):
        self.old_board = copy.deepcopy(self.current_board)

    def place_rooms(self):
        instructions = \
            "Rooms cannot overlap and each room must touch at least" \
            + " two other rooms.\n" \
            + "Use < arrow keys > to move, < , . > to rotate, < space >" \
            + " to switch to the next room, < [ ] > to zoom, and < enter > to end."

        if len(self.screen.choices) == 0:
            self.screen.choices.append(None)

        # keep track of current room
        current_room = self.screen.choice(0) or self.current_board.rooms[0]
        current_room_index = self.current_board.rooms.index(current_room)

        # if this is the first call to place_rooms, set welcome message
        if not self.screen.choice(0):
            self.current_board.screen.info.text = "{} Moving {} room.\n{}".format(
                'Dark begins by arranging the board.',
                current_room.name,
                instructions,
            )
            self.screen.choices[0] = current_room

        setting_up_board = True
        while setting_up_board:
            self.current_board.flush_hex_data()
            key = self.screen_input.get_keypress(self.current_board.screen)
            if key == None:
                return False
            elif key == " " or key == "l" or key == "n":
                if self.current_board.check_for_collisions(current_room):
                    self.current_board.screen.info.error = "Avoid collisions!"
                else:
                    current_room_index = ((current_room_index + 1) % 7)
                    current_room = self.current_board.rooms[current_room_index]
                    self.screen.choices[0] = current_room
                    self.current_board.screen.info.text = \
                        "Moving {} room.\n{}".format(current_room.name, instructions)
            elif key == "return" or key == "Enter":
                # check to see if board satisfies connectivity rules
                if self.current_board.check_for_collisions(current_room):
                    self.current_board.screen.info.error = "Avoid collisions!"
                else:
                    connected, msg = self.current_board.connectivity_test()
                    if not connected:
                        self.current_board.screen.info.error = "Invalid board arrangement. " + msg
                    else:
                        setting_up_board = False
            else:
                current_room.keyboard_movement(key)
                self.current_board.screen.info.error = None

        self.current_board.screen.info.error = None
        self.current_board.end_turn(actions=None)
        return True

    def choose_first_player(self):
        first_faction = self.screen_input.choose_from_list(
            self.screen,
            ['Light', 'Dark'],
            'Light chooses who goes first'
        )
        if first_faction == None:
            return False
        elif first_faction == 'Dark':
            self.current_board.end_turn(actions=None)
        return True

    def place_players(self):
        player_spots = self.current_board.get_all_hexes()

        if not self.screen.choice(0):
            hex1 = self.screen_input.choose_hexes(
                self.current_board.screen,
                player_spots,
                prompt_text = "Click to place the {} player".format(self.current_board.faction)
            )
            if hex1 == None:
                return False
            self.current_board.move_object(self.get_current_player(), to_hex=hex1)
            self.current_board.flush_player_data()
            self.current_board.end_turn(actions=None)

        player_spots.remove(self.screen.choice(0) or hex1)

        hex2 = self.screen_input.choose_hexes(
            self.current_board.screen,
            player_spots,
            prompt_text = "Now click to place the {} player".format(self.current_board.faction)
        )
        if hex2 == None:
            return False
        self.current_board.move_object(self.get_current_player(), to_hex=hex2)
        self.current_board.end_turn()
        # self.sync_boards() # handle in play / do_action
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
            except InvalidMove as error:
                self.screen.info.error = '{}'.format(move)
        self.end_game()
        self.screen.info.error = "Click on any hex to exit"
        self.screen_input.get_click(self.screen)

    def end_game(self):
        self.current_board.game_over = True
        winning_faction = self.is_game_over()
        if winning_faction:
            self.screen.info.text = "WINNER: {}!".format(winning_faction)
        else:
            current_faction = self.current_board.faction
            self.screen.info.text = '{} forfeits, {} wins!'.format(
                current_faction,
                other_faction(current_faction),
            )
        self.save_to_file()
        return True

    def call_action(self):
        action = self.screen.data['current_action']

        request_player = self.screen.data['request_player']
        if request_player == 'All':
            request_player = self.current_board.faction

        if action == 'none':
            # This happens if the user has not selected a new option after
            # the previous one completed
            # print('.none.')
            return
        elif request_player != self.current_board.faction:
            # print('.not_enabled.') # '{} not enabled, returning without calling action'.format(request_player))
            return

        print('[{}] calling action:{}, player:{}'.format(self.game_id, action, request_player))
        self.screen.info.error = None
        done = False
        done_msg = ''

        if action == 'move':
            done = self.move()
            done_msg = 'Done moving'
        elif action == 'bless':
            done = self.bless()
            done_msg = 'Done blessing'
        elif action == 'drop':
            done = self.drop()
            done_msg = 'Done dropping'
        elif action == 'pick up':
            done = self.pick_up()
            done_msg = 'Done picking up'
        elif action == 'cast spell':
            done = self.cast_spell()
            done_msg = 'Done casting'
        elif action == 'end turn':
            # TODO: only ask for confirmation if there are unused actions/spells
            confirmation = self.screen.choice(0) or self.screen_input.choose_from_list(
                self.screen,
                ['Yes', 'No'],
                'Are you sure you want end your turn?'
            )
            if confirmation == 'Yes':
                done = self.end_turn()
                done_msg = 'Now it\'s {}\'s turn'.format(self.current_board.faction)
            elif confirmation == 'No':
                done = True
                done_msg = 'Not ending turn'
        elif action == 'reset turn':
            done = self.reset_turn()
            done_msg = 'Turn reset'
        elif action == 'place rooms':
            done = self.place_rooms()
            done_msg = 'Board setup done'
        elif action == 'choose first player':
            done = self.choose_first_player()
            done_msg = '{} places first'.format(self.current_board.faction)
        elif action == 'place players':
            done = self.place_players()
            done_msg = 'Player setup done'
        elif action == 'maybe end game':
            confirmation = self.screen_input.choose_from_list(
                self.screen,
                ['Yes', 'No'],
                'Are you sure you want to forfeit and quit?'
            )
            if confirmation == 'Yes':
                self.current_board.game_over = True
                done = True
                winning_faction = self.is_game_over()
                if winning_faction:
                    done_msg = "WINNER: {}!".format(winning_faction)
                else:
                    current_faction = self.current_board.faction
                    done_msg = '{} forfeits, {} wins!'.format(
                        current_faction,
                        other_faction(current_faction),
                    )
            elif confirmation == 'No':
                # self.screen.info.text = 'Not ending game. {}'.format(start_msg)
                # self.screen.data['current_action'] = self.start_action
                # self.screen.action_buttons_on = False
                # self.screen.choices = []
                done = True
                done_msg = 'Not ending game'

        print('[{}] called action:{}, done:{}'.format(self.game_id, action, done))

        if done:
            select_option_text = 'Select an option (click button or use keybinding)'

            self.screen.data['current_action'] = 'none'
            self.screen.info.text = '{}. {}'.format(done_msg, select_option_text)
            self.screen.action_buttons_on = True # TODO: redundant??
            self.screen.choices = []

            if action == 'place rooms':
                self.start_action = 'choose first player'
                self.screen.data['current_action'] = 'choose first player'
                self.screen.info.text = '{}. {}'.format(done_msg, 'Light chooses who goes first')
                self.screen.action_buttons_on = False
                self.sync_boards()

                if 'choice_idx' in self.screen.data:
                    self.screen.data.pop('choice_idx')
                self.choose_first_player()
            elif action == 'choose first player':
                self.start_action = 'place players'
                self.screen.data['current_action'] = 'place players'
                self.screen.info.text = '{}. {}'.format(done_msg, 'Click to place the Light player')
                self.screen.action_buttons_on = False
                self.sync_boards()

                if 'click_x' in self.screen.data:
                    self.screen.data.pop('click_x')
                self.place_players()
            elif action == 'place players':
                self.start_action = 'none'
                self.screen.info.text = '{}! {} goes first.\n{}'.format(
                    done_msg,
                    self.current_board.faction,
                    select_option_text,
                )
                self.screen.reset_on = True
                self.sync_boards()
            elif action == 'maybe end game' and self.current_board.game_over:
                self.start_action = 'end game'
                self.screen.data['current_action'] = 'end game'
                self.screen.info.text = done_msg

            self.save_to_file()

    def get_game_state(self, include_metadata=False):
        action = self.screen.data['current_action'] if self.screen.data else 'none'

        if include_metadata:
            data = {
                'game_id': self.game_id,
                'created': self.created,
                'updated': self.updated,
                'start_action': self.start_action,
            }
        else:
            data = {}

        data.update({
            'info': self.screen.info.text,
            'error': self.screen.info.error,
            'reset_on': self.screen.reset_on,
            'current_action': action,

            'game_over': self.current_board.game_over,
            'current_player': self.current_board.faction,
            'actions_remaining': self.current_board.actions,
            'hexes': self.current_board.return_hex_data(),
            'spells': self.current_board.return_spell_data(),
        })
        return data

    # main method for js frontend
    # TODO: check is_game_over at needed points in spells
    def do_action(self, data):
        self.updated = Game.current_time_str()
        self.screen.data = data

        try:
            self.call_action()
        except InvalidMove as error:
            self.screen.info.text = 'Select an option (click button or use keybinding)'
            self.screen.info.error = 'INVALID MOVE: {}'.format(error)
            self.screen.choices = []
            self.screen.action_buttons_on = True
            self.screen.data['current_action'] = 'none'

        if self.is_game_over():
            self.start_action = 'end game'
            self.screen.data['current_action'] = 'end game'
            self.end_game()

        # print('[{}] do_action return, action:{}'.format(self.game_id, self.screen.data['current_action']))
        return self.get_game_state()


if __name__ == "__main__":
    piously = Game("Dark")
    piously.play()
