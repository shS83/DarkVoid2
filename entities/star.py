import random
import pygame as pg
import config as c


class Star(pg.sprite.Sprite):
	def __init__(self):
		super().__init__()

		size = random.choice([1, 1, 1, 2, 2, 3])
		self.image = pg.Surface((size, size), pg.SRCALPHA)
		pg.draw.circle(self.image, (220, 220, 255), (size // 2, size // 2), size // 2)

		self.rect = self.image.get_rect()
		self.rect.x = random.randint(0, c.WIDTH)
		self.rect.y = random.randint(0, c.HEIGHT)

		self.speed = random.randint(80, 420)

	def update(self, dt):
		self.rect.y += self.speed * dt

		if self.rect.top > c.HEIGHT:
			self.rect.x = random.randint(0, c.WIDTH)
			self.rect.y = random.randint(-40, -5)
			self.speed = random.randint(80, 420)
