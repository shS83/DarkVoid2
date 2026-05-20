import pygame as pg
import config as c
import random


class PowerUp(pg.sprite.Sprite):
	def __init__(self, game, pos, kind="spread"):
		super().__init__()
		self.image = pg.Surface((46, 46), pg.SRCALPHA)
		self.game = game
		self.kinds = [{"spread": f"{c.HOME_DIR}/assets/powerup-spread.png"}, {
			"health": f"{c.HOME_DIR}/assets/powerup-health.png"}, {"speed": f"{c.HOME_DIR}/assets/powerup-speed.png"}]
		self.kind = random.choice(["spread", "health", "speed"])
		self.kinduint = random.randint(0, 2)
		self.pos = pg.Vector2(pos)
		self.rect = self.image.get_rect(center=self.pos)
		self.speed = 120
		self.direction = 1
		self.duration = 15
		result = self.kinds[self.kinduint].get(self.kind, f"{c.HOME_DIR}/assets/powerup-health.png")
		self.image.blit(pg.image.load(result), (0, 0))
		self.mask = None

	def draw(self, pos):
		self.mask = self.image.copy()
		self.pos = pg.Vector2(pos)
		self.game.screen.blit(self.image, (pos))

	# pg.draw.circle(self.image, (180, 180, 255), (16, 16), 16)
	# font = pg.font.SysFont("monospace", 12)
	# pg.draw.circle(self.image, (255, 255, 255), (13, 13), 12)
	# print(self.kind)
	# if self.kind == "spread":
	# 	message = font.render("🂳", True, (0, 0, 0), (255, 255, 255))
	# if self.kind == "health":
	# 	message = font.render("💚", True, (255, 255, 255), (0, 0, 0))
	# if self.kind == "speed":
	# 	message = font.render("㉏", True, (255, 0, 0), (255, 255, 255))
	# else:
	# 	message = font.render("?", True, (255, 255, 255), (0, 0, 0))
	# self.image.blit(message, (0, 0))
	# self.game.screen.blit(self.image, (pos))

	def update(self, dt):
		self.duration -= dt
		self.pos.y += self.speed * dt
		self.pos.x += self.speed * dt
		self.rect = self.pos
		if self.pos.x >= c.WIDTH or self.pos.x <= 0:
			self.direction = -self.direction
		if self.pos.y >= c.HEIGHT or self.pos.y <= 0:
			self.direction = -self.direction

		print(self.pos)
		if self.duration <= 0:
			self.kill()
