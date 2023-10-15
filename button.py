import pygame as pg
import consts

class Menu:
    pass
class Board:
    pass

class Button:
    def __init__(self, centerx, centery, text,
                    FG_color = consts.FG_BTN_COLOR, BG_color = consts.BG_BTN_COLOR,
                    width = consts.BTN_WIDTH, height = consts.BTN_HEIGHT,
                    font_size = consts.BTN_TEXT_SIZE, type = Menu(), active = True):
        pg.init()
        self.active = active
        self.centerx = centerx
        self.centery = centery

        self.BG_color = BG_color
        self.FG_color = FG_color

        self.width = width
        self.height = height

        self.rel_x = centerx - self.width // 2
        self.rel_y = centery - self.height // 2
        if isinstance(type, Menu):
            self.abs_x = self.rel_x + (consts.WIDTH + 2 * consts.MARGIN - consts.END_GAME_MENU_SIZE) // 2
            self.abs_y = self.rel_y + (consts.HEIGHT + 2 * consts.HEADER - consts.END_GAME_MENU_SIZE) // 2
        elif isinstance(type, Board):
            self.abs_x = self.rel_x
            self.abs_y = self.rel_y
        self.rect = (self.rel_x, self.rel_y, self.width, self.height)

        font = pg.font.Font("Helvetica.otf", font_size)
        self.text = font.render(text, True, consts.WHITE)
    def draw(self, surface: pg.Surface, mouse_pos: tuple[int]):
        if self.isOver(mouse_pos):
           rect = (self.rel_x + consts.BTN_BORDER, self.rel_y + consts.BTN_BORDER, self.width - 2 * consts.BTN_BORDER, self.height - 2 * consts.BTN_BORDER)
           pg.draw.rect(surface, self.BG_color, self.rect)
           pg.draw.rect(surface, self.FG_color, rect)
        else:
           pg.draw.rect(surface, self.FG_color, self.rect)

        surface.blit(self.text, (self.centerx - self.text.get_width()//2, self.centery - self.text.get_height()//2))

    def isOver(self, mouse_pos: tuple[int]):
        x, y = mouse_pos
        return self.abs_x < x < self.abs_x + self.width and self.abs_y < y < self.abs_y + self.height and self.active
