"""
Used to display spell info on the screen. Hovering over a spell shows its
description, and spells also show their faction, artwork, and tapped state.

Color and font properties are hard coded.
"""
import pygame as pg

# TODO: dont dup colors from screen
ROOM_COLORS = {
    "P" : pg.Color("pink"),
    "I" : pg.Color("slateblue"),
    "O" : pg.Color("orange"),
    "U" : pg.Color("saddlebrown"),
    "S" : pg.Color("turquoise2"),
    "L" : pg.Color("yellowgreen"),
    "Y" : pg.Color("yellow2"),
}

TRANSPARENT = (0, 0, 0, 0)
BLACK     = (  0,   0,   0)
WHITE     = (255, 255, 255)
DARKGRAY  = ( 64,  64,  64)
GRAY      = (128, 128, 128)
LIGHTGRAY = (212, 208, 200)

FACTION_COLORS = {
    "Dark": BLACK,
    "Light": WHITE,
    None: pg.Color("snow2"),
}

FONT = "Arial"
FONT_SIZE = 24

class Spell(object):
    def __init__(self, rect, name, description, description_pos, faction, artwork, tapped, screen):
        self.rect = rect
        self.name = name
        self.description = description
        self.description_pos = description_pos
        self.screen = screen # screen obj to draw on
        self.faction = faction
        self.unplaced_artwork = artwork
        self.tapped = tapped
        self.hovered = False

        self.text_color = BLACK
        self.font = pg.font.SysFont(FONT, FONT_SIZE)

        # surface objs for spell
        self.surface = pg.Surface(self.rect.size)
        self.spell_label = None
        self.spell_label_rect = None

    def handle_event(self, event):
        if event.type == pg.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                self.hovered = True
            else:
                self.hovered = False

    def render_text(self):
        antialias = True

        # write spell name on spell box
        w, h = self.rect.size # spell box dimensions
        text_surface = self.font.render(self.name, antialias, self.text_color)
        text_rect = text_surface.get_rect()

        # faction indicator extends 3*h2 into the box - center text in remaining space
        # h2 = int(h / 2)
        # text_width = w - 3*h2
        # text_rect.center = (3*h2 + int(text_width / 2), h2)
        # self.surface.blit(text_surface, text_rect)

        # left align text a bit in from left of box, center vertically
        h2 = int(h / 2)
        text_rect.midleft = (5, h2)
        self.surface.blit(text_surface, text_rect)

        # write spell description at description_pos
        description_txt = ' {}'.format(self.description)
        self.spell_label = self.font.render(description_txt, antialias, self.text_color)
        self.spell_label_rect = self.spell_label.get_rect(topleft=self.description_pos)

    def draw(self):
        self.screen.blit(self.surface, self.rect)
        if self.hovered:
            self.screen.blit(self.spell_label, self.spell_label_rect)

    def update(self):
        # background
        self.surface.fill(FACTION_COLORS[None])

        # cross out tapped spells
        if self.tapped:
            h2 = int(self.rect.height/2)
            pg.draw.line(self.surface, BLACK, (0, h2), (self.rect.width, h2), 1.5)

        # faction
        if self.faction:
            w, h = self.rect.size
            h2 = int(h/2)

            # left flag
            # points = [(0, 0), (0, h), (h2, h), (3*h2, h2), (h2, 0)]

            # right flag
            points = [(w, 0), (w, h), (w-h2, h), (w-3*h2, h2), (w-h2, 0)]

            pg.draw.polygon(self.surface, FACTION_COLORS[self.faction], points, 0)
            pg.draw.polygon(self.surface, BLACK, points, 1) # outline

        # artwork
        if self.unplaced_artwork:
            color = ROOM_COLORS[self.name[0]]
            other_color = BLACK
            radius = 10
            pad = int(self.rect.height/2)
            center = (self.rect.width - pad, pad)
            pg.draw.circle(self.surface, other_color, center, radius+1) # outline
            pg.draw.circle(self.surface, color, center, radius)

        # outline on spell name rectangle
        pg.draw.rect(self.surface, DARKGRAY, pg.Rect((0, 0), self.rect.size), 1)

        # text last so it is on top
        self.render_text()
