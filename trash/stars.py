import pygame as pg
from core.spritegroups import star_group
from core import commons as c
import pygame.gfxdraw
import random
import entities.events as events
from entities.events import Event


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
		if len(star_group) > 500:
			Eventing = Event.INITIATION

	def move(self, screen):
		self.x += self.size / 1.5

	def draw(self, screen):
		c.screen.blit(self.surface, (self.x, self.y))


def starfield(width, height, single=False):
	global star_group
	for i in range(1000):
		# Star(random.randint(0, width), random.randint(-10, -1), random.randint(1, 3), (255, 0, 0)))
		# if i % 3 > 0.5:
		# stray = Star.move(c.screen)
		# star_group.add(stray)
		star_group.add(Star(random.randint(0, width), random.randint(-10, -1), random.randint(1, 3),
		                    (255, 255, 0)))


def roll_the_drops():
	star_group.update(c.screen)
	star_group.draw(c.screen)
	for s in star_group:
		s.rect.y += 1
		if s.rect.y > c.screen.get_height():
			star_group.remove(s)


def starfields():
	for star in star_group:
		star.rect.y += 1
		if star.rect.y > c.screen.get_height():
			star_group.remove(star)
		if len(star_group) > 500:
			Event = Event.INITIATION

	starfield(random.randint(1, c.screen.get_width()), random.randint(1, c.screen.get_height()), single=False)
