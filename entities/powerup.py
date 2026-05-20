import pygame as pg
import config as c


class PowerUp(pg.sprite.Sprite):
	def __init__(self, game, pos, kind="spread"):
		super().__init__()
		self.image = pg.Surface((26, 26), pg.SRCALPHA)
		self.game = game
		self.kind = kind
		self.pos = pg.Vector2(pos)
		self.rect = self.image.get_rect(center=self.pos)
		self.speed = 120

	def draw_powerup(self, pos):
		pg.draw.circle(self.image, (180, 180, 255), (8, 8), 16)
		font = pg.font.SysFont("monospace", 12)
		pg.draw.circle(self.image, (255, 255, 255), (8, 8), 12)
		message = font.render(self.image, True, True, (0, 0, 0), (255, 255, 255))
		self.image.blit(message, (0, 0))

	def update(self, dt):
		self.pos.y += self.speed * dt
		self.rect.center = self.pos

		if self.rect.top > c.HEIGHT:
			self.kill()
