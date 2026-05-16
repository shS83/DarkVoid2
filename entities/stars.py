import pygame as pg
from core.spritegroups import star_group
from core import config as c
import pygame.gfxdraw
import random


class Star:

	def __init__(self, x, y, size, color):
		self.x = x
		self.y = y
		self.size = size
		self.color = color
		self.surface = pg.Surface((size, size)).convert_alpha()
		pg.gfxdraw.filled_circle(self.surface, int(size // 4), int(size // 4), int(size // 4), color)

	def update(self, screen):
		self.y += self.size / 1.3
		if self.y > c.screen.get_height():
			jig = star_group.index(self)
			star_group.pop(jig)

	def move(self, screen):
		self.x += self.size / 1.5

	def draw(self, screen):
		c.screen.blit(self.surface, (self.x, self.y))


def starfield(width, height, single=False):
	global star_group
	for i in range(100):
		star_group.get(Star(random.randint(0, width), random.randint(-10, -1), random.randint(1, 3), (255, 0, 0)))
	if single:
		star_group = star_group
	for star in star_group:
		star.rect.y += 1


starfield(random.randint(1, c.screen.get_width()), random.randint(1, c.screen.get_height()), single=False)
