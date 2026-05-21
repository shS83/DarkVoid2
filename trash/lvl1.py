import pygame as pg
import os
import pygame.gfxdraw
import random
import math
import core.commons as c
from entities.player import Player, PlayerBullet
from entities.asteroid import Meteor
from game import Game
from core.spritegroups import asteroid_group

pg.init()
screen = pg.display.set_mode((1920, 1080), pg.SRCALPHA)
pg.display.set_caption("DARK VOID 2")
clock = pg.time.Clock()
all_sprites = pg.sprite.Group()
asteroids = pg.sprite.Group()
running = True
dt = clock.tick(60) / 1000

# enterprise = Player(dt, (1920 // 2, 1080 // 2 - 200))

# while running:
for _ in range(10):
	asteroidi = Meteor(game := Game(), (random.randint(0, c.WIDTH), random.randint(0, c.HEIGHT)))
	asteroid_group.add(asteroidi)
	all_sprites.add(asteroidi)

keys = pg.key.get_pressed()
mouse = pg.mouse.get_pressed()
direction = pg.Vector2(0, 0)

if keys[pg.K_LEFT] or keys[pg.K_a]:
	direction.x -= 1
if keys[pg.K_RIGHT] or keys[pg.K_d]:
	direction.x += 1
if keys[pg.K_UP] or keys[pg.K_w]:
	direction.y -= 1
if keys[pg.K_DOWN] or keys[pg.K_s]:
	direction.y += 1
if keys[pg.K_SPACE] or mouse[0] == 1:
	if Player.shoot_mode == "spread":
		Player.shoot_spread()
	else:
		Player.shoot_normal()
if keys[pg.K_ESCAPE]:
	running = False
for _ in range(10):
	asteroidi = Meteor(game := Game(), (random.randint(0, c.WIDTH), random.randint(0, c.HEIGHT)))

while running:
	screen.blit(pg.image.load(f'{c.HOME_DIR}/assets/01362_overtime_1920x1080.jpg').convert_alpha(), (0, 0))
	dt = clock.tick(60) / 1000
	asteroidi.update(dt)

	asteroid_group.add(asteroidi)
	all_sprites.add(asteroidi)

	pg.display.flip()
