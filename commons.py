import pygame as pg
from pygame.locals import *
import os
from darkvoid2 import State, Level
from typing import Tuple
import pygame.gfxdraw, random, math

x_res = 1920
y_res = 1080
HOME_DIR = os.path.expanduser('~') + '/PycharmProjects/DarkVoid2'
pg.init()
screen = pygame.display.set_mode([x_res, y_res], pg.SRCALPHA)
pygame.display.set_caption("Dark Void 2")
pygame.init()
clock = pygame.time.Clock()
running = True
laserinterval = 3
laserkey = 0
keyinterval = 5
keypress = 0
message = ""
blastinterval = 1000
last = 0
ASTEROID_COUNT = 5
MAX_ASTEROIDS = 10
MIN_ASTEROID_DISTANCE = 200
asteroids = []
curr_state = State.WAITINGFORGAME
ASTEROIDS = []
laserkey = 0
SCORE = 0
ROCK1 = pygame.image.load(f'{HOME_DIR}/assets/rock_3_2.png').convert_alpha()
ROCK2 = pygame.image.load(f'{HOME_DIR}/assets/rock_4_2.png').convert_alpha()
ROCK3 = pygame.image.load(f'{HOME_DIR}/assets/rock_5_2.png').convert_alpha()
ROCK4 = pygame.image.load(f'{HOME_DIR}/assets/rock_6_2.png').convert_alpha()
ROCK5 = pygame.image.load(f'{HOME_DIR}/assets/rock_3.png').convert_alpha()
ROCK6 = pygame.image.load(f'{HOME_DIR}/assets/rock_4.png').convert_alpha()
BACKGROUND = pygame.image.load(f'{HOME_DIR}/assets/01362_overtime_1920x1080.jpg').convert_alpha()
ROCK_IMAGES = [ROCK1, ROCK2, ROCK3, ROCK4, ROCK5, ROCK6]
render_cache: dict[Tuple[int, int, int], pg.Surface] = {}
t = pg.time.get_ticks() * 0.001
ship_scale = 0.3
frame = 0
STARS = []
ANIMATIONS = []
PARTICLES = []
STREAMS = []
BULLETS = []
ASTEROIDS = []
SHIP = pg.image.load(f"{HOME_DIR}/assets/ship_neutral_2.png", "Ship neutral").convert_alpha()
ship_x, ship_y = screen.get_width() // 2, screen.get_height() - SHIP.get_height() - 50
SHIP_L1 = pg.image.load(f"{HOME_DIR}/assets/ship_left_1.png", "Ship left").convert_alpha()
SHIP_L2 = pg.image.load(f"{HOME_DIR}/assets/ship_left_2.png", "Ship left").convert_alpha()
SHIP_L3 = pg.image.load(f"{HOME_DIR}/assets/ship_left_3.png", "Ship left").convert_alpha()
SHIP_L4 = pg.image.load(f"{HOME_DIR}/assets/ship_left_4.png", "Ship left").convert_alpha()
SHIP_R1 = pg.image.load(f"{HOME_DIR}/assets/ship_right_1.png", "Ship right").convert_alpha()
SHIP_R2 = pg.image.load(f"{HOME_DIR}/assets/ship_right_2.png", "Ship right").convert_alpha()
SHIP_R3 = pg.image.load(f"{HOME_DIR}/assets/ship_right_3.png", "Ship right").convert_alpha()
SHIP_R4 = pg.image.load(f"{HOME_DIR}/assets/ship_right_4.png", "Ship right").convert_alpha()
LASER_IMAGE = pg.image.load(f'{HOME_DIR}/assets/laser.png', "Laser beam").convert_alpha()
LASER_IMAGE = pg.transform.rotate(LASER_IMAGE, 145)
LASER_IMAGE2 = pg.image.load(f'{HOME_DIR}/assets/laser_2.png', "Laser beam 2").convert_alpha()
LASER_IMAGE2 = pg.transform.rotate(LASER_IMAGE2, 145)
level = Level()
now = pg.time.get_ticks()
