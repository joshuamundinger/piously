class MockTextbox(object):
    def __init__(self):
        self.text = ''
        self.error = ''

class MockScreen(object):
    def __init__(self):
        self.info = MockTextbox()
        self.board_state = MockTextbox()

        self.player_data = []
        self.hex_data = []
        self.artwork_data = []
        self.aura_data = []
        self.active_hexes = []

        # used for pygame mode
        self.key = None
        self.click_hex = None

        self.data = None
        self.action_buttons_on = True
        self.reset_on = False
        self.choices = []

    def loop_once(self):
        pass

    def make_map(self, data):
        pass

    def make_spells(self, data):
        pass

    def toggle_action_buttons(self):
        pass

    def choice(self, idx):
        try:
            return self.choices[idx]
        except IndexError:
            return None
