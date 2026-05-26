import pygame as pg
import config as c
from pathlib import Path

class PlayerBullet(pg.sprite.Sprite):
	def __init__(self, game, pos, image=pg.image.load(Path(c.HOME_DIR, "assets", "laser.png")).convert_alpha(), velocity=(0, -800)):
		super().__init__()

		self.game = game
		self.pos = pos
		self.velocity = pg.Vector2(velocity)
		self.image = image

		self.rect = self.image.get_rect()
		self.damage = 1

	def update(self, dt = pg.time.Clock().tick(60)/1000):
		self.pos += self.velocity * dt
		self.rect.center = self.pos

		if self.rect.bottom < 0 or self.rect.top > c.HEIGHT or self.rect.left < 0 or self.rect.right > c.WIDTH:
			self.kill()


class EnemyBullet(pg.sprite.Sprite):
	def __init__(self, game, pos, velocity):
		super().__init__()

		self.game = game
		self.pos = pg.Vector2(pos)
		self.velocity = pg.Vector2(velocity)

		self.image = pg.Surface((12, 12), pg.SRCALPHA)
		pg.draw.circle(self.image, (255, 80, 120), (6, 6), 9)

		self.rect = self.image.get_rect()
		self.radius = 9

	def update(self, dt):
		self.pos += self.velocity * dt
		self.rect.center = self.pos

		if (
				self.rect.top > c.HEIGHT
				or self.rect.bottom < 0
				or self.rect.right < 0
				or self.rect.left > c.WIDTH
		):
			self.kill()
