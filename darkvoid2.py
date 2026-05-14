import pygame as pg
from pygame.locals import *
from create_ship import create_spaceship_image
from PIL import Image, ImageDraw
import pygame.gfxdraw, random, math
from pygame.math import Vector2
from pygame.transform import rotozoom
import pox_module, pfx_module
import lvl_module
import hs_module

# import intro_module
# Do an intro

pg.init()

screen = pg.display.set_mode((1280, 720))


SHIP = pg.image.load("spaceship_neutral.png")
SHIP_L = pg.image.load("spaceship_left.png")
SHIP_R = pg.image.load("spaceship_right.png")
running = True
count = 0
clock = pg.time.Clock()

while running:
    screen.fill((0, 0, 0))
    screen.blit(SHIP, (640, 640))
    for event in pg.event.get():
        if event.type == QUIT:
            running = False
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            running = False

    pg.display.flip()
    count += 1
    clock.tick(159)
