import pygame as pg
import os

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
PLAYER_BULLET_SPEED = 350
PLAYER_HITBOX_RADIUS = 4
WIDTH = 1920
HEIGHT = 1080
BOSS_TIME = False
HOME_DIR = "/home/shs/PycharmProjects/DarkVoid2"
MSG_FONT = pg.font.SysFont(f'{HOME_DIR}/PycharmProjects/DarkVoid2/assets/GoMonoNerdFontPropo-Bold.ttf',
                           60)
GOTHIC_FONT = pg.font.Font(f'{HOME_DIR}/assets/VL-Gothic-Regular.ttf', 36)
