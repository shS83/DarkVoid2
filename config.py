import pygame as pg
import os
from entities.level import Level
from entities.events import Event

pg.init()
pg.mixer.init()
pg.mixer.music.set_volume(0.2)

x_res = 1920
y_res = 1080
screen = pg.display.set_mode((x_res, y_res), pg.SRCALPHA)
FPS = 60
DEBUG = True
PLAYER_SPEED = 420
PLAYER_FOCUS_SPEED = 180
PLAYER_FIRE_COOLDOWN = 0.08
ENEMY_BULLET_SPEED = 180
ENEMY_HP = 5
PLAYER_BULLET_SPEED = 350
PLAYER_HITBOX_RADIUS = 4
HOME_DIR = os.path.dirname(__file__)
ROCK1 = pg.image.load(f'{HOME_DIR}/assets/rock_1.png').convert_alpha()
ROCK2 = pg.image.load(f'{HOME_DIR}/assets/rock_2.png').convert_alpha()
ROCK3 = pg.image.load(f'{HOME_DIR}/assets/rock_3.png').convert_alpha()
ROCK4 = pg.image.load(f'{HOME_DIR}/assets/rock_4.png').convert_alpha()
ROCK5 = pg.image.load(f'{HOME_DIR}/assets/rock_5.png').convert_alpha()
ROCK6 = pg.image.load(f'{HOME_DIR}/assets/rock_6.png').convert_alpha()

BEACH1 = pg.image.load(f'{HOME_DIR}/assets/beach_1.jpg').convert()
BEACH2 = pg.image.load(f'{HOME_DIR}/assets/beach_2.jpg').convert()
BEACH3 = pg.image.load(f'{HOME_DIR}/assets/beach_3.jpg').convert()
BEACH4 = pg.image.load(f'{HOME_DIR}/assets/beach_4.jpg').convert()
BEACHES=[BEACH1, BEACH2, BEACH3, BEACH4]
BACKGROUND = BEACH3
ROCK_IMAGES = [ROCK1, ROCK2, ROCK3, ROCK4, ROCK5, ROCK6]
WIDTH = 1920
HEIGHT = 1080
BOSS_TIME = False
SCALE = 0.4
HOME_DIR = os.path.dirname(__file__)
MSG_FONT = pg.font.SysFont(f'{HOME_DIR}/PycharmProjects/DarkVoid2/assets/GoMonoNerdFontPropo-Bold.ttf',
                           60)
GOTHIC_FONT = pg.font.Font(f'{HOME_DIR}/assets/VL-Gothic-Regular.ttf', 36)
Event = Event.INITIATION
level = Level()
Level.stage = 1