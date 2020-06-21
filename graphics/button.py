"""
Used to display clickable buttons on the screen

Color and font properties are currently hard coded
"""

import pygame as pg

BLACK     = (  0,   0,   0)
WHITE     = (255, 255, 255)
DARKGRAY  = ( 64,  64,  64)
GRAY      = (128, 128, 128)
LIGHTGRAY = (212, 208, 200)
BUTTON_COLOR = pg.Color("lightblue1")
DISABLED_COLOR = pg.Color("snow2")

FONT = "Arial"
FONT_SIZE = 24

class Button(object):
    def __init__(self, rect, text, keybinding, screen, disabled=False):
        # text is both what the button displays
        # and what it returns if clicked / keybinding is pressed
        self.rect = rect
        self.text = text
        self.error = None
        self.keybinding = keybinding # typing this will 'click' button
        self.screen = screen # screen obj to draw on
        self.disabled = disabled

        self.color = BUTTON_COLOR
        self.disabled_color = DISABLED_COLOR
        self.text_color = BLACK
        self.font = pg.font.SysFont(FONT, FONT_SIZE)

        # state of button
        self.clicked = False
        self.hovered = False
        self.lastMouseDownOverButton = False

        # surface objs for each button state
        self.surfaceNormal = pg.Surface(self.rect.size)
        self.surfaceDisabled = pg.Surface(self.rect.size)
        self.versions = [self.surfaceNormal, self.surfaceDisabled]

        # TODO: add mouseover behavior
        # self.surfaceDown = pg.Surface(self.rect.size)
        # self.surfaceHighlight = pg.Surface(self.rect.size)

    def handle_event(self, event):
        if self.disabled:
            return None

        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return self.text
            else:
                return None
        elif event.type == pg.KEYDOWN:
            if pg.key.name(event.key) == self.keybinding:
                return self.text
            else:
                return None

    def draw(self):
        if self.disabled:
            self.screen.blit(self.surfaceDisabled, self.rect)
        else:
            self.screen.blit(self.surfaceNormal, self.rect)

    def render_text(self):
        if self.keybinding:
            text = '{} ({})'.format(self.text, self.keybinding)
        else:
            text = self.text

        antialias = True
        w = self.rect.width
        h = self.rect.height

        surf1 = self.font.render(text, antialias, self.text_color)
        rect1 = surf1.get_rect()
        rect1.center = int(w / 2), int(h / 2)

        # render second line with error text
        if self.error:
            rect1.center = int(w / 2), int(h / 3)

            surf2 = self.font.render(self.error, antialias, self.text_color)
            rect2 = surf2.get_rect()
            rect2.center = int(w / 2), int(3*h / 4)
            self.surfaceNormal.blit(surf2, rect2)
            self.surfaceDisabled.blit(surf2, rect2)


        self.surfaceNormal.blit(surf1, rect1)
        self.surfaceDisabled.blit(surf1, rect1)

    def render_bevel(self, surface):
        w = self.rect.width
        h = self.rect.height

        pg.draw.line(surface, WHITE, (1, 1), (w - 2, 1))
        pg.draw.line(surface, WHITE, (1, 1), (1, h - 2))
        pg.draw.line(surface, DARKGRAY, (1, h - 1), (w - 1, h - 1))
        pg.draw.line(surface, DARKGRAY, (w - 1, 1), (w - 1, h - 1))
        pg.draw.line(surface, GRAY, (2, h - 2), (w - 2, h - 2))
        pg.draw.line(surface, GRAY, (w - 2, 2), (w - 2, h - 2))


    def update(self):
        # TODO: loop over views instead of duplicating code
        # fill background color for all buttons
        self.surfaceNormal.fill(self.color)
        self.surfaceDisabled.fill(self.disabled_color)

        w = self.rect.width
        h = self.rect.height

        # draw caption text for all buttons
        self.render_text()

        # normal button gets black border with bevel
        pg.draw.rect(self.surfaceNormal, BLACK, pg.Rect((0, 0, w, h)), 1)
        self.render_bevel(self.surfaceNormal)

        # disabled button gets black border
        pg.draw.rect(self.surfaceDisabled, BLACK, pg.Rect((0, 0, w, h)), 1)
