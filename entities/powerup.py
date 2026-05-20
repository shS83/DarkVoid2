import pygame as pg
import config as c
import random
from core.utils import get_random_position, get_random_velocity
from entities.glitter import Glitter


class PowerUp(pg.sprite.Sprite):
	def __init__(self, game, pos, kind="spread"):
		super().__init__()
		self.glitter_timer = 0
		self.game = game
		self.kind = kind
		self.pos = get_random_position(c.screen)
		self.velocity = get_random_velocity(10, 360)
		self.speed = 120
		self.effects = pg.sprite.Group()
		self.all_sprites = pg.sprite.LayeredUpdates()

		path = f"{c.HOME_DIR}/assets/powerup-{kind}.png"
		self.image = pg.image.load(path).convert_alpha()
		self.image = pg.transform.scale(self.image, (46, 46))

		self.rect = self.image.get_rect(center=self.pos)

	def update(self, dt):
		self.pos.y += self.speed * dt
		self.rect.center = self.pos

		self.glitter_timer -= dt

		if self.glitter_timer <= 0:
			self.glitter_timer = 0.5

			glitter_pos = (
				self.rect.centerx + random.randint(-24, 24),
				self.rect.centery + random.randint(-24, 24)
			)

			glitter = Glitter(self.game, glitter_pos)
			self.effects.add(glitter)
			self.all_sprites.add(glitter)

		if self.rect.top > c.HEIGHT:
			self.kill()
