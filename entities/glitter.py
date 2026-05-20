import random
import pygame as pg


class Glitter(pg.sprite.Sprite):
	def __init__(self, game, pos):
		super().__init__()

		self.game = game
		self.pos = pg.Vector2(pos)

		self.life = random.uniform(0.25, 0.55)
		self.max_life = self.life
		self.size = random.randint(2, 4)

		self.image = pg.Surface((self.size, self.size), pg.SRCALPHA)
		pg.draw.circle(
			self.image,
			(255, 255, random.randint(120, 255)),
			(self.size // 2, self.size // 2),
			self.size // 2
		)

		self.rect = self.image.get_rect(center=self.pos)

	def update(self, dt):
		self.life -= dt

		if self.life <= 0:
			self.kill()
			return

		self.pos.y -= 20 * dt
		self.rect.center = self.pos

		self.image.set_alpha(int(255 * (self.life / self.max_life)))
