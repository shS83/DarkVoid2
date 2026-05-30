import math
import pygame as pg
import config as c


class Shield(pg.sprite.Sprite):
	def __init__(self, game, player):
		super().__init__()

		self.game = game
		self.player = player

		self.life = 5.0
		self.max_life = self.life

		self.angle = 0
		self.rotation_speed = 180

		self.base_image = pg.transform.smoothscale(
			c.PALLO3,
			(210, 210)
		).convert_alpha()

		self.image = self.base_image.copy()
		self.image.set_alpha(120)
		self.rect = self.image.get_rect(center=self.player.rect.center)

	def update(self, dt):
		self.life -= dt

		if self.life <= 0:
			self.player.shield_active = False
			self.kill()
			return

		self.angle += self.rotation_speed * dt

		center = self.player.rect.center

		self.image = pg.transform.rotozoom(
			self.base_image,
			self.angle,
			1.0
		)

		alpha = int(95 + 45 * math.sin(pg.time.get_ticks() * 0.012))
		alpha = max(70, min(145, alpha))

		self.image.set_alpha(alpha)

		self.rect = self.image.get_rect(center=center)