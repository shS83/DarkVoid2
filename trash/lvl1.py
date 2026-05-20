import pygame as pg
import os
import pygame.gfxdraw
import random
import math
import core.commons as c
from entities.player import *

pg.init()
screen = pg.display.set_mode((1920, 1080), pg.SRCALPHA)
pg.display.set_caption("DARK VOID 2")
clock = pg.time.Clock()
running = True
dt = clock.tick(60) / 1000
enterprise = Player(dt, (1920 // 2, 1080 // 2 - 200))

while running:
	enterprise.update(dt)

	screen.blit(pg.image.load(f'{c.HOME_DIR}/assets/space_background_2.jpg').convert_alpha(), (0, 0))

	pg.display.flip()
