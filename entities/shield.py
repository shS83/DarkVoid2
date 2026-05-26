import random
import pygame as pg
import config as c
from entities.glitter import Glitter

class Shield(pg.sprite.Sprite):
    def __init__(self, game, player):
        super().__init__()
        self.glitter_timer = 0.25
        self.game = game
        self.player = player

        self.image = pg.transform.scale(
            c.PALLO3,
            (210, 210)
        ).convert_alpha()

        self.image.set_alpha(100)

        self.rect = self.image.get_rect(center=self.player.rect.center)

        self.life = 5.0

    def update(self, dt):
        if self.glitter_timer <= 0:
            self.glitter_timer = 0.005
        self.life -= dt
        self.glitter_timer -= dt
        for _ in range(16):
            glitter_pos = (
                self.rect.centerx + random.randint(-100, 100),
                self.rect.centery + random.randint(-100, 100),
            )

            glitter = Glitter(self.game, glitter_pos)
            self.game.effects.add(glitter)
            self.game.all_sprites.add(glitter)

        if self.life <= 0:
            self.player.shield_active = False
            self.kill()
            return

        self.rect.center = self.player.rect.center