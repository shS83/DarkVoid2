import random
import pygame as pg
import config as c
from entities.glitter import Glitter


class PowerUp(pg.sprite.Sprite):
	def __init__(self, game, pos, kind=None):
		super().__init__()

		self.game = game
		self.kind = kind or random.choice(["spread", "health", "speed", "laser"])
		self.pos = pg.Vector2(pos)

		path = f"{c.HOME_DIR}/assets/powerup-{self.kind}.png"
		self.image = pg.image.load(path).convert_alpha()
		self.image = pg.transform.scale(self.image, (46, 46))
		self.size = random.randint(4, 8)
		self.rect = self.image.get_rect(center=self.pos)

		self.speed = 120
		self.duration = 15
		self.glitter_timer = 0

	def update(self, dt):
		self.duration -= dt

		self.pos.y += self.speed * dt
		self.rect.center = self.pos

		self.glitter_timer -= dt

		if self.glitter_timer <= 0:
			self.glitter_timer = 0.025

			for _ in range(4):
				glitter_pos = (
					self.rect.centerx + random.randint(-26, 26),
					self.rect.centery + random.randint(-26, 26),
				)

				glitter = Glitter(self.game, glitter_pos)
				self.game.effects.add(glitter)
				self.game.all_sprites.add(glitter)

		if self.rect.top > c.HEIGHT or self.duration <= 0:
			self.kill()
