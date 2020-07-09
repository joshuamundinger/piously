'''
This file implements a display for Piously using pygame

credit to Mekire for the starting code - https://github.com/Mekire/hex_pygame_redit
'''
from backend.helpers import other_faction
from graphics.button import Button, TextBox
from graphics.spell import Spell
from numpy import average, sqrt, unique
from sys import exit
import pygame as pg

BACKGROUND = pg.Color("white")
SCREEN_SIZE = (800, 600)
TRANSPARENT = (0, 0, 0, 0)
FPS = 10 # 60
FONT = "Arial"

ROOMS = ["P", "I", "O", "U", "S", "L", "Y", "Shovel", "Temp"]

ROOM_COLORS = {
    "P" : pg.Color("pink"),
    "I" : pg.Color("slateblue"),
    "O" : pg.Color("orange"),
    "U" : pg.Color("saddlebrown"),
    "S" : pg.Color("turquoise2"),
    "L" : pg.Color("yellowgreen"),
    "Y" : pg.Color("yellow2"),
    "Shovel" : pg.Color("tan"),
    "Temp": pg.Color("white"),
}

FACTION_COLORS = {
    "Dark" : pg.Color("black"),
    "Light" : pg.Color("white"),
}

# define hex size and shape
S = 12 # half side length of hex
H = int(S*sqrt(3)) # half height of hex
HEX_POINTS = (0, H), (S, 0), (3*S, 0), (4*S, H), (3*S, 2*H), (S, 2*H)
HEX_FOOTPRINT = (4*S+1, 2*H+1) # adding one so that the outlines don't get cut off
ROW_OFFSET = 0, 2*H
COL_OFFSET = 3*S, H

# define button size and shape
BUTTON_SIZE = (int((SCREEN_SIZE[0]-1)/4)-1, 30) # 4 buttons across but with room for 1px padding
SPELL_SIZE = (150, 30)
HOVER_TEXT_POS = (5, 2*BUTTON_SIZE[1] + 5)

# TODO:
# - indicate valid hexes to click visually
# - make the player object prettier
#   - https://www.google.com/url?sa=i&url=https%3A%2F%2Fdlpng.com%2Fpng%2F4443758&psig=AOvVaw0OV8088DkAY7x2EFMcegXh&ust=1592797306363000&source=images&cd=vfe&ved=0CAIQjRxqFwoTCODByL_-keoCFQAAAAAdAAAAABAM
# - move some classes into seperate files
# - improve handle_click to use mask not rect (right now it will sometimes take wrong hex)
# - figure out + probably remove layer
# - make spells clickable
class HexTile(pg.sprite.Sprite):
    def __init__(self, pos, room, axial_pos, *groups):
        # *groups is initialized as pg.sprite.LayeredUpdates()
        super(HexTile, self).__init__(*groups)
        self.color =  ROOM_COLORS[room]
        self.image = self.make_tile(room)
        self.rect = self.image.get_rect(center=pos)
        self.mask = self.make_mask()
        self.room = room
        self.layer = 0 # used to control the render order of the hex_tiles
        self.axial_pos = axial_pos

    def name(self):
        return '{}: ({}, {})'.format(self.room, self.axial_pos[0], self.axial_pos[1])

    def make_tile(self, room):
        image = pg.Surface(HEX_FOOTPRINT).convert_alpha()
        image.fill(TRANSPARENT)
        pg.draw.polygon(image, self.color, HEX_POINTS)
        pg.draw.lines(image, pg.Color("black"), 1, HEX_POINTS, 2)
        return image

    def make_mask(self):
        temp_image = pg.Surface(self.image.get_size()).convert_alpha()
        temp_image.fill(TRANSPARENT)
        pg.draw.polygon(temp_image, pg.Color("red"), HEX_POINTS)
        return pg.mask.from_surface(temp_image)

# When the mouse is over a HexTile, displays the room + coordinates of the
# hex and changes the color of the hex slightly
class HexHover(pg.sprite.Sprite):
    COLOR = (50, 50, 200, 150) # transparent blue

    def __init__(self, *groups):
        super(HexHover, self).__init__(*groups)
        self.image = pg.Surface(HEX_FOOTPRINT).convert_alpha()
        self.image.fill(TRANSPARENT)
        pg.draw.polygon(self.image, self.COLOR, HEX_POINTS)

        self.rect = pg.Rect((0,0,1,1))
        self.mask = pg.Mask((1,1))
        self.mask.fill()
        self.target = None
        self.hex = None
        self.hex_label = None
        self.hex_label_rect = None
        self.font = pg.font.SysFont(FONT, 24)

    def update(self, pos, hex_tiles, screen_rect):
        self.rect.topleft = pos
        hits = pg.sprite.spritecollide(self, hex_tiles, 0, pg.sprite.collide_mask)
        if hits:
            true_hit = max(hits, key=lambda x: x.rect.bottom)
            self.target = true_hit.rect.topleft
            self.hex = true_hit.room

            # diplay the room info for the hovered hex
            self.hex_label = text_render(true_hit.name(), self.font)

            # to make text follow hex_hover pass midbottom=pos to get_rect
            # or midbottom=screen_rect.midbottom to put at bottom of screen
            self.hex_label_rect = self.hex_label.get_rect(topleft=HOVER_TEXT_POS)
            self.hex_label_rect.clamp_ip(screen_rect)
        else:
            self.hex = None

    def draw(self, surface):
        if self.hex:
            surface.blit(self.image, self.target)
            surface.blit(self.hex_label, self.hex_label_rect)

class PygameScreen(object):
    def __init__(self):
        pg.init()
        pg.display.set_mode(SCREEN_SIZE)
        pg.display.set_caption('Piously')

        self.screen = pg.display.get_surface()
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()

        # variables for rendering the board of hex tiles
        self.hex_tiles = None
        self.hex_data = None
        self.axial_avg_x = 0
        self.axial_avg_y = 0
        self.hex_hover = HexHover()

        # variables for rendering game objects
        self.spells = []
        self.spell_data = []
        self.player_data = []
        self.artwork_data = []
        self.aura_data = []

        # variables for backend to read
        self.key = None # most recent keypress
        self.click_hex = None # axial pos of clicked hex

        # text boxes
        w, h = SPELL_SIZE
        W, H = SCREEN_SIZE
        self.board_state = TextBox(pg.Rect((0, 0), (w, 2*h)), self.screen)
        self.info = TextBox(pg.Rect((w, 0), (W-w, 2*h)), self.screen)

        # buttons
        w, h = BUTTON_SIZE
        w, h = w + 1, h + 1 # add padding between buttons
        self.action_buttons = [
            Button(pg.Rect((2, H-2*h), BUTTON_SIZE), 'move', '1', self.screen),
            Button(pg.Rect((2+w, H-2*h), BUTTON_SIZE), 'bless', '2', self.screen),
            Button(pg.Rect((2+2*w, H-2*h), BUTTON_SIZE), 'drop', '3', self.screen),
            Button(pg.Rect((2+3*w, H-2*h), BUTTON_SIZE), 'pick up', '4', self.screen),
            Button(pg.Rect((2, H-h), BUTTON_SIZE), 'cast spell', 'q', self.screen),
            Button(pg.Rect((2+w, H-h), BUTTON_SIZE), 'end turn', 'w', self.screen),
            Button(pg.Rect((2+2*w, H-h), BUTTON_SIZE), 'reset turn', 'e', self.screen),
            Button(pg.Rect((2+3*w, H-h), BUTTON_SIZE), 'end game', 'r', self.screen),
        ]
        self.buttons = self.action_buttons + [self.info, self.board_state]

        self.choices = [] # needed for interoperability with js_screen

    # noop method needed for interoperability with js_screen
    def choice(self, choice_idx):
        return None

    def toggle_action_buttons(self):
        # assumes all action buttons have the same disabled state
        new_state = not self.action_buttons[0].disabled
        for button in self.action_buttons:
            button.disabled = new_state

    # TODO: maybe replace this with a draw method that updates the positions
    # rather than making new objects when the board changes?
    def make_map(self, hexes):
        # hexes is a list of hashes each with
        #  'x': int, x-coord axial
        #  'y': int, y-coord axial
        #  'room': string, which room the hex is in
        hex_tiles = pg.sprite.LayeredUpdates()

        # used to center tiles on the screen
        self.axial_avg_x = int(average(unique([hex['x'] for hex in hexes])))
        self.axial_avg_y = int(average(unique([hex['y'] for hex in hexes])))

        for hex in hexes:
            pos = self.axial_to_screen(hex['x'], hex['y'])
            HexTile(pos, hex['room'], (hex['x'], hex['y']), hex_tiles)

        self.hex_tiles = hex_tiles

    def make_spells(self, spell_data):
        spells = []
        for idx, spell in enumerate(spell_data):
            # putting buttons in column along the left
            # pos = (0, 3*SPELL_SIZE[1] + idx*SPELL_SIZE[1])

            # putting buttons in column along the right
            w, h = SPELL_SIZE
            W = SCREEN_SIZE[0]
            pos = (W-w, 3*h + idx*(h-1))
            spell_obj = Spell(
                rect = pg.Rect(pos, SPELL_SIZE),
                name = spell['name'],
                description = spell['description'],
                description_pos = HOVER_TEXT_POS,
                faction = spell['faction'],
                tapped = spell['tapped'],
                artwork = spell['artwork'],
                screen = self.screen
            )
            spells.append(spell_obj)
        self.spells = spells

    def axial_to_screen(self, x, y):
        # put the (axial_avg_x, axial_avg_y) hex in the center
        start_x, start_y = self.screen_rect.center
        x_idx = x - self.axial_avg_x
        y_idx = y - self.axial_avg_y

        rowsize_x, rowsize_y = ROW_OFFSET
        colsize_x, colsize_y = COL_OFFSET

        pos = (
            start_x + (rowsize_x * x_idx) + (colsize_x * y_idx),
            start_y + (rowsize_y * x_idx) + (colsize_y * y_idx),
        )
        return pos

    def draw_players(self):
        # player_data is a list of hashes each with
        #  'x': int, x-coord axial of player's hex
        #  'y': int, y-coord axial of player's hex
        #  'faction': string, player's faction
        for player in self.player_data:
            color = FACTION_COLORS[player['faction']]
            other_color = FACTION_COLORS[other_faction(player['faction'])]
            center = self.axial_to_screen(player['x'], player['y'])
            radius = 10
            pg.draw.circle(self.screen, other_color, center, radius+1)
            pg.draw.circle(self.screen, color, center, radius)

    def draw_artworks(self):
        # artwork_data is a list of hashes each with
        #  'x': int, x-coord axial of artwork's hex
        #  'y': int, y-coord axial of artwork's hex
        #  'room': string, 1 letter name for artwork's room
        for artwork in self.artwork_data:
            color = ROOM_COLORS[artwork['room']]
            other_color = FACTION_COLORS["Dark"]
            center = self.axial_to_screen(artwork['x'], artwork['y'])
            radius = 10
            pg.draw.circle(self.screen, other_color, center, radius+1)
            pg.draw.circle(self.screen, color, center, radius)

    def draw_auras(self):
        # aura_data is a list of hashes each with
        #  'x': int, x-coord axial of player's hex
        #  'y': int, y-coord axial of player's hex
        #  'faction': string, player's faction
        for aura in self.aura_data:
            color = FACTION_COLORS[aura['faction']]
            other_color = FACTION_COLORS[other_faction(aura['faction'])]
            center = self.axial_to_screen(aura['x'], aura['y'])
            radius = 15
            pg.draw.circle(self.screen, other_color, center, radius+1)
            pg.draw.circle(self.screen, color, center, radius)

    def update(self):
        [button.update() for button in self.buttons]
        [spell.update() for spell in self.spells]
        if self.hex_tiles:
            for sprite in self.hex_tiles:
                if sprite.layer != sprite.rect.bottom:
                    self.hex_tiles.change_layer(sprite, sprite.rect.bottom)
            self.hex_hover.update(pg.mouse.get_pos(), self.hex_tiles, self.screen_rect)

    def render(self):
        self.screen.fill(BACKGROUND)
        [button.draw() for button in self.buttons]
        [spell.draw() for spell in self.spells]
        if self.hex_tiles:
            self.hex_tiles.draw(self.screen)
            self.hex_hover.draw(self.screen)
            self.draw_auras()
            self.draw_players()
            self.draw_artworks()
        pg.display.update()

    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.close()

            # send events to buttons and spells so they can update state
            for button in self.action_buttons:
                if button.handle_event(event):
                    self.key = button.text
                    return
            for spell in self.spells:
                spell.handle_event(event)

            # store most recent click / keypress for backend to read
            if event.type == pg.MOUSEBUTTONDOWN:
               self.handle_click(event.pos)
            elif event.type == pg.KEYDOWN:
                self.key = pg.key.name(event.key)

    def close(self):
        pg.quit()
        exit()

    def handle_click(self, pos):
        for hex in self.hex_tiles:
            if hex.rect.collidepoint(pos):
                self.click_hex = hex.axial_pos
                return

    # main game loop
    def loop_once(self):
        self.event_loop()
        self.update()
        self.render()
        self.clock.tick(FPS)

def text_render(text, font, color=pg.Color("black")):
    text_rend = font.render(text, 1, color)
    text_rect = text_rend.get_rect()
    image = pg.Surface(text_rect.size).convert_alpha()
    image.fill(TRANSPARENT)
    image.blit(text_rend, text_rect)
    return image
