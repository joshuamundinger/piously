class MockTextbox(object):
    def __init__(self):
        self.text = ''
        self.error = ''

class MockScreen(object):
    def __init__(self):
        self.info = MockTextbox()
        self.board_state = MockTextbox()

        # used for pygame mode
        self.player_data = []
        self.hex_data = []
        self.artwork_data = []
        self.aura_data = []
        self.key = None
        self.click_hex = None
        self.action_buttons_on = True

        # used for js mode
        self.active_hexes = []
        self.data = None
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
