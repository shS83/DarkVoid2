import pygame as pg
import config as c


class PlayerBullet(pg.sprite.Sprite):
	def __init__(self, game, pos, velocity=(0, -800)):
		super().__init__()

		self.game = game
		self.pos = pos
		self.velocity = pg.Vector2(velocity)
		self.image = pg.image.load(f"{c.HOME_DIR}/assets/laser.png").convert_alpha()

		self.rect = self.image.get_rect(center=pos)
		self.damage = 1

	def update(self, dt):
		self.pos += self.velocity * dt
		self.rect.center = self.pos

		if self.rect.bottom < 0:
			self.kill()


class EnemyBullet(pg.sprite.Sprite):
	def __init__(self, game, pos, velocity):
		super().__init__()

		self.game = game
		self.pos = pg.Vector2(pos)
		self.velocity = pg.Vector2(velocity)

		self.image = pg.Surface((12, 12), pg.SRCALPHA)
		pg.draw.circle(self.image, (255, 80, 120), (6, 6), 6)

		self.rect = self.image.get_rect(center=self.pos)
		self.radius = 6

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
