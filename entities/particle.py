import random
import math
import pygame as pg
import config as c


class Particle(pg.sprite.Sprite):
	def __init__(self, game, pos):
		super().__init__()

		self.game = game
		self.pos = pg.Vector2(pos)

		angle = random.uniform(0, math.tau)
		speed = random.uniform(180, 1050)

		self.velocity = pg.Vector2(
			math.cos(angle),
			math.sin(angle)
		) * speed

		self.gravity = pg.Vector2(0, 100)

		self.life = random.uniform(0.25, 0.95)
		self.max_life = self.life

		self.size = random.randint(2, 5)

		self.image = pg.Surface((self.size, self.size), pg.SRCALPHA)
		pg.draw.circle(
			self.image,
			(255, random.randint(120, 220), 40),
			(self.size // 2, self.size // 2),
			self.size // 2
		)

		self.rect = self.image.get_rect(center=self.pos)
		self.screen_rect = pg.Rect(0, 0, c.WIDTH, c.HEIGHT)

	def update(self, dt):
		self.life -= dt

		if self.life <= 0:
			self.kill()
			return

		self.velocity += self.gravity * dt
		self.pos += self.velocity * dt

		self.velocity *= 0.96

		self.rect.center = self.pos

		if not self.screen_rect.colliderect(self.rect):
			self.kill()
			return

		alpha = int(255 * (self.life / self.max_life))
		self.image.set_alpha(alpha)
