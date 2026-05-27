import pygame as pg
import config as c
from pathlib import Path
from entities.glitter import Glitter
c.HOME_DIR = Path(__file__).parent.parent.absolute()

class PlayerBullet(pg.sprite.Sprite):
	def __init__(self, game, pos, image=pg.image.load(Path(c.HOME_DIR, "assets", "laser.png")).convert_alpha(), velocity=(0, -800)):
		super().__init__()
		self.image = image
		self.game = game
		self.pos = pg.Vector2(pos)
		self.rect = self.image.get_rect(center=self.pos)
		self.velocity = pg.Vector2(velocity)
		self.damage = 1

	def update(self, dt = pg.time.Clock().tick(60)/1000):
		self.pos += self.velocity * dt
		self.rect.center = self.pos

		if self.rect.bottom < 0 or self.rect.top > c.HEIGHT or self.rect.left < 0 or self.rect.right > c.WIDTH:
			self.kill()


class EnemyBullet(pg.sprite.Sprite):
	def __init__(self, game, pos, velocity):
		super().__init__()
		self.image = pg.Surface((16, 16), pg.SRCALPHA)
		self.game = game
		self.pos = pg.Vector2(pos)
		self.rect = self.image.get_rect(center=self.pos)
		self.velocity = pg.Vector2(velocity)
		self.radius = 8
		pg.draw.circle(self.image, (60, 0, 0), (6, 6), self.radius)
		pg.draw.circle(self.image, (255, 0, 0), (6, 6), self.radius - 2)
		pg.draw.circle(self.image, (255, 80, 120), (6, 6), self.radius - 4)
		pg.draw.circle(self.image, (255, 255, 160), (6, 6), self.radius - 6)


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
