import math
import pygame as pg
import random
import config as c


class SpiralEffect(pg.sprite.Sprite):
	def __init__(self, pos):
		super().__init__()

		self.pos = pg.Vector2(pos)
		self.time = 0

		self.image = pg.Surface((1920, 1024), pg.SRCALPHA)
		self.rect = self.image.get_rect(center=self.pos)
		self.rando = 0.55
		self.radius = 12
		self.counter = 0

	def update(self, dt):
		self.time += dt

		center = pg.Vector2(
			c.screen.get_width() // 2,
			c.screen.get_height() // 2
		)

		amount = 1024
		value = -0.01
		value2 = -0.1
		value3 = -1
		direction = -1
		running = True
		self.image.fill((0, 0, 0, 15))
		alpha = 255
		color = (255, 255, 255, alpha)
		color2 = (0, 0, 255, alpha)

		if self.counter > 256 and self.counter < 513:
			color = (120, 255, 120, alpha)
			color2 = (255, 255, 120, alpha)
			value3 = -value3
		elif self.counter > 512 and self.counter < 785:
			color = (120, 120, 255, alpha)
			color2 = (255, 120, 120, alpha)
			value3 = -value3
		elif self.counter > 784 and self.counter < 1024:
			color = (255, 255, 255, alpha)
			color2 = (255, 0, 0, alpha)
		elif self.counter > 1023:
			self.counter = 0
		self.counter += 1
		for i in range(amount):
			radius = i * math.atan(self.radius) * self.radius
			angle = self.time * 4 + i * self.rando
			alpha = max(30, 255 - i * 4)
			self.rando -= value2
			if self.rando > 5:
				value2 = -value2
			self.radius -= value
			if self.radius < 2:
				value = -value
			elif self.radius > 18:
				value = -value
			x = center.x + math.cos(angle) * radius
			y = center.y + math.sin(angle) * radius
			x2 = center.x + math.cos(angle + math.pi) * radius
			y2 = center.y + math.sin(angle + math.pi) * radius
			size = 2 + int(i * 0.08)
			pg.draw.circle(
				self.image,
				color2,
				(int(x2), int(y2)),
				size
			)

			pg.draw.circle(
				self.image,
				color,
				(int(x), int(y)),
				size
			)
running = True
spiral = SpiralEffect((c.WIDTH // 2, c.HEIGHT // 2))
tick = pg.time.Clock()
while running:
	for e in pg.event.get():
		if (e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE) or e.type == pg.QUIT:
			running = False
#	c.screen.fill((0, 0, 0, 0))
	c.screen.blit(spiral.image, (0,0))
	dt = tick.tick(60) / 1000
	SpiralEffect.update(spiral, dt)
	pg.display.flip()
