import pygame as pg


class RainbowText:
    """Move a spectrum from upper left to lower right through a text mask."""

    def __init__(self, text_mask, period=512, speed=300):
        self.text_mask = text_mask
        self.period = period
        self.speed = speed
        height = text_mask.get_height()
        self.tile = pg.Surface((period, height))
        for diagonal in range(period + height):
            color = pg.Color(0, 0, 0)
            color.hsva = ((diagonal % period) * 360 / period, 65, 100, 100)
            pg.draw.line(self.tile, color, (diagonal, 0), (diagonal - height, height))
        self.surface = pg.Surface(text_mask.get_size(), pg.SRCALPHA)

    def render(self, elapsed):
        offset = int(elapsed * self.speed) % self.period
        for x in range(-self.period + offset, self.surface.get_width(), self.period):
            self.surface.blit(self.tile, (x, 0))

        self.surface.blit(self.text_mask, (0, 0), special_flags=pg.BLEND_RGBA_MULT)
        return self.surface
