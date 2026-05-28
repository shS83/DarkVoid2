import random
import pygame as pg
import config as c
from entities.glitter import Glitter


class Shield(pg.sprite.Sprite):
	def __init__(self, game, player):
		super().__init__()

		self.game = game
		self.player = player

		self.image = pg.transform.scale(
			c.PALLO3,
			(210, 210)
		).convert_alpha()

		self.image.set_alpha(125)
		self.rect = self.image.get_rect(center=self.player.rect.center)

		self.life = 5.0
		self.glitter_timer = 0.0

	def update(self, dt):
		self.life -= dt
		self.glitter_timer -= dt

		if self.life <= 0:
			self.player.shield_active = False
			self.kill()
			return

		self.rect.center = self.player.rect.center

		if self.glitter_timer <= 0:
			self.glitter_timer = 0.04

			for _ in range(3):
				glitter_pos = (
					self.rect.centerx + random.randint(-90, 90),
					self.rect.centery + random.randint(-90, 90),
				)

				glitter = Glitter(self.game, glitter_pos)
				self.game.effects.add(glitter)
				self.game.all_sprites.add(glitter)