import pygame as pg
import config as c


class PlayerBullet(pg.sprite.Sprite):
	def __init__(self, game, pos):
		super().__init__()

		self.game = game

		self.image = pg.Surface((6, 20), pg.SRCALPHA)
		pg.draw.rect(self.image, (100, 220, 255), (0, 0, 6, 20))

		self.rect = self.image.get_rect(center=pos)
		self.pos = pg.Vector2(self.rect.center)

		self.velocity = pg.Vector2(0, -800)

	def update(self, dt):
		self.pos += self.velocity * dt
		self.rect.center = self.pos

		if self.rect.bottom < 0:
			self.kill()


class EnemyBullet(pg.sprite.Sprite):
	def __init__(self, game, pos, velocity):
		super().__init__()
		self.game = game
		self.image = pg.Surface((12, 12), pg.SRCALPHA)
		pg.draw.circle(self.image, (255, 80, 120), (6, 6), 6)
		self.rect = self.image.get_rect(center=pos)
		self.pos = pg.Vector2(pos)
		self.vel = pg.Vector2(velocity)
		self.radius = 6

	def update(self, dt):
		self.pos += self.vel * dt
		self.rect.center = self.pos

		if (
				self.rect.right < -40 or self.rect.left > c.WIDTH + 40 or
				self.rect.bottom < -40 or self.rect.top > c.HEIGHT + 40
		):
			self.kill()
