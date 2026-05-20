import pygame as pg
from pygame import Vector2
import random
from typing import Tuple
from core import commons as c


def wrap_position(pos, rect, margin=0):
	return Vector2(
		pos.x % (rect.width + margin),
		pos.y % (rect.height + margin)
	)


def get_random_position(surface):
	return Vector2(
		random.randrange(surface.get_width()),
		random.randrange(surface.get_height()),
	)


def get_random_velocity(min_speed, max_speed):
	speed = random.randint(min_speed, max_speed)
	angle = random.randrange(0, 360)
	return Vector2(speed, 0).rotate(angle)


# Icon
def render_char(ch: str, color: Tuple[int, int, int], fontsize: int = 36) -> pg.Surface:
	key = (ch, color)
	font = pg.font.SysFont("VL-Gothic-Regular.ttf", fontsize, bold=True)
	surf = font.render(ch, True, color)
	return surf


def clamp(v, lo, hi):
	return max(lo, min(hi, v))


def zoom_text(msg, color, opacity, rot=1.00, sca=1.00, zoomfont=c.msg_font):
	fs = zoomfont.render(msg, True, color)
	rotated = pg.transform.rotozoom(fs, rot, sca)
	rotated.set_alpha(opacity)
	xd = rotated.get_width()
	yd = rotated.get_height()
	return rotated, c.x_res / 2 - xd / 2, c.y_res / 2 - yd / 2
