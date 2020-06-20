'''
This file implements a display for piously using pygame

credit to Mekire on github for the starting code
https://github.com/Mekire/hex_pygame_redit
'''
from sys import exit
import pygame as pg
from backend.helpers import other_faction

BACKGROUND = pg.Color("white")
SCREEN_SIZE = (600, 400)
FPS = 10 # 60
FONT = "Arial"

ROOMS = ["P", "I", "O", "U", "S", "L", "Y"]

ROOM_COLORS = {
    "P" : pg.Color("pink"),
    "I" : pg.Color("mediumpurple4"),
    "O" : pg.Color("orange"),
    "U" : pg.Color("saddlebrown"),
    "S" : pg.Color("turquoise2"),
    "L" : pg.Color("yellowgreen"),
    "Y" : pg.Color("yellow2"),
}

FACTION_COLORS = {
    "Dark" : pg.Color("black"),
    "Light" : pg.Color("white"),
}

HEX_POINTS = (8,4), (45,0), (64,10), (57,27), (20,31), (0,22)
HEX_FOOTPRINT = (65, 32)

class HexTile(pg.sprite.Sprite):
    def __init__(self, pos, room, name, *groups):
        # *groups is initialized as pg.sprite.LayeredUpdates()
        super(HexTile, self).__init__(*groups)
        self.color =  ROOM_COLORS[room]
        self.image = self.make_tile(room)
        self.rect = self.image.get_rect(topleft=pos)
        self.mask = self.make_mask()
        self.room = room
        self.layer = 0
        self.coordinate_str = name

    def name(self):
        return ' {}: {}'.format(self.room, self.coordinate_str)

    def make_tile(self, room):
        image = pg.Surface(HEX_FOOTPRINT).convert_alpha()
        pg.draw.polygon(image, self.color, HEX_POINTS)
        pg.draw.lines(image, pg.Color("black"), 1, HEX_POINTS, 2)
        return image

    def make_mask(self):
        temp_image = pg.Surface(self.image.get_size()).convert_alpha()
        pg.draw.polygon(temp_image, pg.Color("red"), HEX_POINTS)
        return pg.mask.from_surface(temp_image)

class CursorHighlight(pg.sprite.Sprite):
    COLOR = (50, 50, 200, 150) # transparent blue

    def __init__(self, *groups):
        super(CursorHighlight, self).__init__(*groups)
        self.image = pg.Surface(HEX_FOOTPRINT).convert_alpha()
        pg.draw.polygon(self.image, self.COLOR, HEX_POINTS)
        self.rect = pg.Rect((0,0,1,1))
        self.mask = pg.Mask((1,1))
        self.mask.fill()
        self.target = None
        self.hex = None
        self.label_image = None
        self.label_rect = None
        self.font = pg.font.SysFont(FONT, 24)

    def update(self, pos, tiles, screen_rect):
        self.rect.topleft = pos
        hits = pg.sprite.spritecollide(self, tiles, 0, pg.sprite.collide_mask)
        if hits:
            true_hit = max(hits, key=lambda x: x.rect.bottom)
            self.target = true_hit.rect.topleft
            self.hex = true_hit.room
            self.label_image = text_render(true_hit.name(), self.font)

            # to make text follow cursor pass midbottom=pos to get_rect
            # or midbottom=screen_rect.midbottom to put at bottom of screen
            self.label_rect = self.label_image.get_rect()
            self.label_rect.clamp_ip(screen_rect)
        else:
            self.hex = None

    def draw(self, surface):
        if self.hex:
            surface.blit(self.image, self.target)
            surface.blit(self.label_image, self.label_rect)

class PiouslyApp(object):
    def __init__(self):
        pg.init()
        pg.display.set_mode(SCREEN_SIZE)

        self.screen = pg.display.get_surface()
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.cursor = CursorHighlight()
        self.hex_data = None
        self.tiles = None
        self.player_data = None
        self.artwork_data = None
        self.aura_data = None
        self.done = False
        self.key = None
        self.click_hex = None
        self.axial_min_x = 0
        self.axial_min_y = 0

    def make_map(self, hexes):
        # hexes is a list of hashes each with
        #  'x': int, x-coord axial
        #  'y': int, y-coord axial
        #  'room': string, which room the hex is in
        tiles = pg.sprite.LayeredUpdates()

        self.axial_min_x = min([hex['x'] for hex in hexes])
        self.axial_min_y = min([hex['y'] for hex in hexes])

        for hex in hexes:
            name = '({}, {})'.format(hex['x'], hex['y'])
            pos = self.axial_to_screen(hex['x'], hex['y'])
            HexTile(pos, hex['room'], name, tiles)

        self.tiles = tiles

    def axial_to_screen(self, x, y):
        # put the (0, 0) hex a bit down and to the left of the top center
        start_x, start_y = self.screen_rect.midtop
        start_x -= 100
        start_y += 50

        # define the x, y offset of the next hex in the row/col
        # hardcoded to make sense based on HEX_POINTS
        row_offset = 12, 27
        col_offset = 57, 5

        pos = (
            start_x + row_offset[0]*(x - self.axial_min_x) + col_offset[0]*(y - self.axial_min_y),
            start_y + row_offset[1]*(x - self.axial_min_x) + col_offset[1]*(y - self.axial_min_y),
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
            topleft = self.axial_to_screen(player['x'], player['y'])
            center = (
                int(topleft[0] + HEX_FOOTPRINT[0]/2),
                int(topleft[1] + HEX_FOOTPRINT[1]/2),
            )
            radius = 10
            pg.draw.circle(self.screen, other_color, center, radius+1)
            pg.draw.circle(self.screen, color, center, radius)

    def draw_artworks(self):
        # artwork_data is a list of hashes each with
        #  'x': int, x-coord axial of artwork's hex
        #  'y': int, y-coord axial of artwork's hex
        #  'room': string, artwork's room
        for artwork in self.artwork_data:
            color = ROOM_COLORS[artwork['room']]
            other_color = FACTION_COLORS["Dark"]
            topleft = self.axial_to_screen(artwork['x'], artwork['y'])
            center = (
                int(topleft[0] + HEX_FOOTPRINT[0]/2),
                int(topleft[1] + HEX_FOOTPRINT[1]/2),
            )
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
            topleft = self.axial_to_screen(aura['x'], aura['y'])
            center = (
                int(topleft[0] + HEX_FOOTPRINT[0]/2),
                int(topleft[1] + HEX_FOOTPRINT[1]/2),
            )
            radius = 15
            pg.draw.circle(self.screen, other_color, center, radius+1)
            pg.draw.circle(self.screen, color, center, radius)

    def update(self):
        if self.tiles:
            for sprite in self.tiles:
                if sprite.layer != sprite.rect.bottom:
                    self.tiles.change_layer(sprite, sprite.rect.bottom)
            self.cursor.update(pg.mouse.get_pos(), self.tiles, self.screen_rect)

    def render(self):
        self.screen.fill(BACKGROUND)
        if self.tiles:
            self.tiles.draw(self.screen)
            self.draw_auras()
            self.draw_players()
            self.draw_artworks()
            self.cursor.draw(self.screen)
        pg.display.update()

    def event_loop(self):
        for event in pg.event.get():
           if event.type == pg.QUIT:
               self.done = True
               self.close()
           elif event.type == pg.MOUSEBUTTONDOWN:
               pass
               # TODO: write handle_click(event.pos) to set self.click_hex
           elif event.type == pg.KEYDOWN:
               self.key = pg.key.name(event.key)
               print("You entered: ({})".format(self.key))

    def loop_once(self):
        self.event_loop()
        self.update()
        self.render()
        self.clock.tick(FPS)

    def close(self):
        pg.quit()
        exit()

def text_render(text, font, color=pg.Color("black")):
    text_rend = font.render(text, 1, color)
    text_rect = text_rend.get_rect()
    image = pg.Surface(text_rect.size).convert_alpha()
    image.blit(text_rend, text_rect)
    return image
