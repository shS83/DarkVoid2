import random
import pygame.transform as tr
import pygame as pg
from pygame import Vector2
import core.commons as c
import math
from typing import Tuple


def get_random_position(rect):
	return Vector2(
		random.randint(rect.left, rect.right),
		random.randint(rect.top, rect.bottom)
	)


def zoom_text(msg, color, opacity, rot=1.00, sca=4.00, zoomfont=c.msg_font):
	fs = zoomfont.render(msg, True, color)
	rotated = tr.rotozoom(fs, rot, sca)
	sca -= 0.05
	rotated.set_alpha(opacity)
	xd = rotated.get_width()
	yd = rotated.get_height()
	c.screen.blit(rotated, (c.screen.get_width() / 2 - xd / 2, c.screen.get_height() / 2 - yd / 2))


def get_random_position(surface):
	return Vector2(
		random.randrange(surface.get_width()),
		random.randrange(surface.get_height()),
	)


def get_random_velocity(min_speed, max_speed):
	speed = random.randint(min_speed, max_speed)
	angle = random.randrange(0, 360)
	return Vector2(speed, 0).rotate(angle)


def angle_to(from_x, from_y, to_x, to_y):
	return math.atan2(to_y - from_y, to_x - from_x)


def render_char(ch: str, color: Tuple[int, int, int]) -> pg.Surface:
	key = (ch, color)
	font = pg.font.SysFont("vl pgothic", 32, bold=True)
	surf = font.render(ch, True, color)
	return surf


def flash_screen(col, screen):
	if col > 1:
		c.screen.fill((int(col), int(col), int(col)))
		col -= 75
	return col


def length2(dx, dy):
	return dx * dx + dy * dy


def clamp(v, lo, hi):
	return max(lo, min(hi, v))


def _get_game_objects():
	game_objects = [*asteroid_group,
	                enterprise, *enemy_group, *bullet_group]
	if enterprise and enterprise.visible:
		game_objects.append(enterprise)
	return game_objects

# Dodonpachi here I come
# camera_offset.y += scroll_speed * dt
# blit_y = (i * tile_height - camera_y) % screen_height
