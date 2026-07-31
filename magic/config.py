import pygame as pg
import os
from pathlib import Path
import sys

pg.init()
pg.mixer.init()
pg.mixer.music.set_volume(0.2)
HOME_DIR = os.path.dirname(__file__)


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parent

    return base_path / relative_path


x_res = 1920
y_res = 1080
screen = pg.display.set_mode((x_res, y_res), pg.SRCALPHA, 32)
FPS = 60
OVERLAY_TIMER = 5000
BOSS_SPAWN_DELAY = 30
PLAYER_SPEED = 500
PLAYER_SUPER_SPEED = 700
PLAYER_FOCUS_SPEED = 180
PLAYER_FIRE_COOLDOWN = 0.08
PLAYER_FIRE_COOLDOWN2 = 0.10
PLAYER_LIVES = 3
PLAYER_FIRE_COOLDOWN3 = 0.17
ENEMY_BULLET_SPEED = 180
ENEMY_BULLET_COOLDOWN = 0.01
PLAYER_BULLET_SPEED = 400
PLAYER_HITBOX_RADIUS = 24
WIDTH = 1920
HEIGHT = 1080
BOSS_TIMER = 2000
DEBUG = False
DEBUG_PLAYER_LIVES = 100
NEXTBOSS = False
SHIELD = False
BOSS_TIME = False
SCALE = 0.35
PLAYER_SCALE = 0.12
PLAYER_INTRO_SCALE = 0.65
PLAYER_INTRO_RISE_TIME = 2.45
PLAYER_INTRO_SCALE_TIME = 2.10
HOME_DIR = os.path.dirname(__file__)
