import pygame as pg
import config as c


class Earth:
	def __init__(self):
		self.image = pg.transform.smoothscale_by(c.EARTH, 0.55)
		self.rect = self.image.get_rect(center=(c.WIDTH // 2, -self.image.get_height() // 2))
		self.target = pg.Vector2(c.WIDTH // 2, c.HEIGHT // 2)
		self.pos = pg.Vector2(self.rect.center)
		self.speed = 120

	def update(self, dt):
		delta = self.target - self.pos
		step = self.speed * dt

		if delta.length() <= step:
			self.pos = self.target
		else:
			self.pos += delta.normalize() * step

		self.rect.center = self.pos

	def draw(self, screen):
		screen.blit(self.image, self.rect)