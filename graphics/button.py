"""
Used to display clickable buttons on the screen. Buttons change color
on hover, can be disabled, and can also be "clicked" via a keybinding.

Color and font properties are hard coded.
"""
import pygame as pg

BLACK     = (  0,   0,   0)
WHITE     = (255, 255, 255)
DARKGRAY  = ( 64,  64,  64)
GRAY      = (128, 128, 128)
LIGHTGRAY = (212, 208, 200)
BUTTON_COLOR = pg.Color("lightblue1")
HOVER_COLOR = pg.Color("lightblue3")
DISABLED_COLOR = pg.Color("snow2")

FONT = "Arial"
FONT_SIZE = 24

class Button(object):
    def __init__(self, rect, text, keybinding, screen, disabled=False):
        # text is both what the button displays
        # and what it returns if clicked / keybinding is pressed
        self.rect = rect
        self.text = text
        self.error = None # displays as a second line under text
        self.keybinding = keybinding # typing this will "click" button
        self.screen = screen # screen obj to draw on
        self.disabled = disabled
        self.hovered = False

        self.color = BUTTON_COLOR
        self.disabled_color = DISABLED_COLOR
        self.hover_color = HOVER_COLOR
        self.text_color = BLACK
        self.font = pg.font.SysFont(FONT, FONT_SIZE)

        # surface objs for each button state
        self.surfaceNormal = pg.Surface(self.rect.size)
        self.surfaceDisabled = pg.Surface(self.rect.size)
        self.surfaceHover = pg.Surface(self.rect.size)
        self.versions = [self.surfaceNormal, self.surfaceDisabled, self.surfaceHover]

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
        elif event.type == pg.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                self.hovered = True
            else:
                self.hovered = False

    def draw(self):
        if self.disabled:
            self.screen.blit(self.surfaceDisabled, self.rect)
        elif self.hovered:
            self.screen.blit(self.surfaceHover, self.rect)
        else:
            self.screen.blit(self.surfaceNormal, self.rect)

    # adds 1 (if not self.error) or 2 (if self.error) lines of text to the button surface
    def render_text(self, surface):
        if self.keybinding:
            text = '{} ({})'.format(self.text, self.keybinding)
        else:
            text = self.text

        antialias = True
        w, h = self.rect.size # button dimensions

        text_surface = self.font.render(text, antialias, self.text_color)
        text_rect = text_surface.get_rect()
        text_rect.center = int(w / 2), int(h / 2) # center text on button

        # render second line with error text
        if self.error:
            text_rect.center = int(w / 2), int(h / 3) # place text above button center

            error_surface = self.font.render(self.error, antialias, self.text_color)
            error_rect = error_surface.get_rect()
            error_rect.center = int(w / 2), int(3*h / 4) # place text below button center

        for version in self.versions:
            version.blit(text_surface, text_rect)

            if self.error:
                version.blit(error_surface, error_rect)

    def render_bevel(self, surface):
        w, h = self.rect.size
        pg.draw.line(surface, WHITE, (1, 1), (w - 2, 1))
        pg.draw.line(surface, WHITE, (1, 1), (1, h - 2))
        pg.draw.line(surface, DARKGRAY, (1, h - 1), (w - 1, h - 1))
        pg.draw.line(surface, DARKGRAY, (w - 1, 1), (w - 1, h - 1))
        pg.draw.line(surface, GRAY, (2, h - 2), (w - 2, h - 2))
        pg.draw.line(surface, GRAY, (w - 2, 2), (w - 2, h - 2))

    def render_button(self, surface, color, bevel=True):
        surface.fill(color)
        pg.draw.rect(surface, BLACK, pg.Rect((0, 0), self.rect.size), 1) # black outline
        if bevel:
            self.render_bevel(surface)

    def update(self):
        self.render_button(self.surfaceNormal, BUTTON_COLOR)
        self.render_button(self.surfaceDisabled, DISABLED_COLOR, bevel=False)
        self.render_button(self.surfaceHover, HOVER_COLOR)

        for surface in self.versions:
            self.render_text(surface)
