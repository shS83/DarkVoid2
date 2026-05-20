import pygame as pg
import config as c


class PowerUp(pg.sprite.Sprite):
	def __init__(self, game, pos, kind="spread"):
		super().__init__()

		self.game = game
		self.kind = kind
		self.pos = pg.Vector2(pos)

		self.image = pg.Surface((26, 26), pg.SRCALPHA)
		pg.draw.circle(self.image, (180, 80, 255), (13, 13), 13)
		pg.draw.circle(self.image, (255, 255, 255), (13, 13), 7)

		self.rect = self.image.get_rect(center=self.pos)
		self.speed = 120

	def update(self, dt):
		self.pos.y += self.speed * dt
		self.rect.center = self.pos

		if self.rect.top > c.HEIGHT:
			self.kill()
