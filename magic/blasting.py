from core import config as c
import pygame as pg
from pox_module import add_charge
from pfx_module import Particle
from poof_module import Smoke
from core.spritegroups import particles_group


def add_one_charge(x, y, amount, last):
	c.now = pg.time.get_ticks()
	if c.now > c.last + c.blastinterval:
		particles_group.add(add_charge(x, y, amount, (255, 255, 255), False))
		c.last = c.now
	return c.last


def add_stream(x, y, amount, color, direction, tolerance, psizemax, opacitydelta, gravity=True,
               secondcolor=(255, 255, 255)):
	for i in range(1, amount):
		if not i % 2:
			particles_group.add(Particle(x, y, secondcolor, direction, tolerance, psizemax, opacitydelta, gravity))
		else:
			particles_group.add(Particle(x, y, color, direction, tolerance, psizemax, opacitydelta, gravity))


def add_smoke(x, y, amount, color=(255, 255, 255), power=15, size=10, lift=13):
	for i in range(1, amount):
		if not i % 10:
			particles_group.add(Smoke(x, y, power, size, color, lift=False))
		else:
			particles_group.add(Smoke(x, y, power, size, (255, 255, 255), lift))
