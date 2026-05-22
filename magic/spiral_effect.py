import math
import pygame as pg
import random
import config as c
from core.spritegroups import effects_group, all_sprites


class SpiralEffect(pg.sprite.Sprite):
	def __init__(self, pos):
		super().__init__()

		self.pos = pg.Vector2(pos)
		self.time = 0

		self.image = pg.Surface((260, 260), pg.SRCALPHA)
		self.rect = self.image.get_rect(center=self.pos)

	def update(self, dt):
		self.time += dt

		# self.image.fill((0, 0, 0, 0))

		center = pg.Vector2(
			c.screen.get_width() // 2,
			c.screen.get_height() // 2
		)

		amount = 48
		running = True

		for i in range(amount):
			radius = i * 8
			#angle = self.time * 4 + i * 0.45
			angle = self.time * 4 + i * 0.55

			x = center.x + math.cos(angle) * radius
			y = center.y + math.sin(angle) * radius
			x2 = center.x + math.cos(angle + math.pi) * radius
			y2 = center.y + math.sin(angle + math.pi) * radius
			size = 2 + int(i * 0.08)
			alpha = max(30, 255 - i * 4)
			color = (120, 180, 255, alpha)

			pg.draw.circle(
				c.screen,
				(255, 120, 220, alpha),
				(int(x2), int(y2)),
				size
			)

			pg.draw.circle(
				c.screen,
				color,
				(int(x), int(y)),
				size
			)
running = True
spiral = SpiralEffect((c.WIDTH // 2, c.HEIGHT // 2))
tick = pg.time.Clock()
while running:
	dt = tick.tick(60) / 1000
	SpiralEffect.update(spiral, dt)
	pg.display.flip()
