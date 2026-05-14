from idlelib.configdialog import is_int

import pygame as pg
from pygame.locals import *
# from PIL import Image, ImageDraw
import pygame.gfxdraw, random, math
from pygame.math import Vector2
from pygame.sprite import collide_rect, collide_circle
from pygame.transform import rotozoom
import pox_module, pfx_module
# import poof_module
# import lvl_module
# import hs_module
from typing import Tuple

# import intro_module
# Do an intro
HOME_DIR = "/home/shs/OneDrive/Documents/Code"
pg.init()

screen = pg.display.set_mode((2000, 1500), SRCALPHA)
STARS = []
ANIMATIONS = []
PARTICLES = []
STREAMS = []
BULLETS = []
SHIP = pg.image.load("ship_neutral.png", "Ship neutral").convert_alpha()
SHIP_L1 = pg.image.load("ship_left_1.png", "Ship left").convert_alpha()
SHIP_L2 = pg.image.load("ship_left_2.png", "Ship left").convert_alpha()
SHIP_L3 = pg.image.load("ship_left_3.png", "Ship left").convert_alpha()
SHIP_L = pg.image.load("ship_left.png", "Ship left").convert_alpha()
SHIP_R1 = pg.image.load("ship_right_1.png", "Ship right").convert_alpha()
SHIP_R2 = pg.image.load("ship_right_2.png", "Ship right").convert_alpha()
SHIP_R3 = pg.image.load("ship_right_3.png", "Ship right").convert_alpha()
SHIP_R = pg.image.load("ship_right.png", "Ship right").convert_alpha()
LASER_IMAGE = pg.image.load(f'{HOME_DIR}/laser_2.png', "Laser beam").convert_alpha()
LASER_IMAGE = pg.transform.rotate(LASER_IMAGE, 145)
running = True
clock = pg.time.Clock()
ship_x, ship_y = screen.get_width() // 2, screen.get_height() - SHIP.get_height() - 50


def wrap_position(position, surface):
	x, y = position
	w, h = surface.get_size()
	return Vector2(x % (w + enterprise.image.get_width()), y % (h + enterprise.image.get_height()))


def angle_to(from_x, from_y, to_x, to_y):
	return math.atan2(to_y - from_y, to_x - from_x)


render_cache: dict[Tuple[int, int, int], pg.Surface] = {}
t = pg.time.get_ticks() * 0.001
ship_scale = 0.3
frame = 0


# Icon
def render_char(ch: str, color: Tuple[int, int, int]) -> pg.Surface:
	key = (ch, color)
	font = pg.font.SysFont("vl pgothic", 32, bold=True)
	surf = font.render(ch, True, color)
	return surf


def clamp(v, lo, hi):
	return max(lo, min(hi, v))


class GameObject:
	def __init__(self, position, sprite, velocity):
		self.position = Vector2(position)
		self.sprite = sprite
		self.radius = sprite.get_width() / 2
		self.velocity = Vector2(velocity)

	def draw(self, surface):
		blit_position = self.position - Vector2(self.radius)
		surface.blit(self.sprite, blit_position)

	def move(self, surface):
		self.position = wrap_position(self.position + self.velocity, surface)

	def collides_with(self, other_obj):
		distance = self.position.distance_to(other_obj.position)
		return distance < self.radius + other_obj.radius

	def collides_with_tolerance(self, other_obj, tolerance):
		distance = self.position.distance_to(other_obj.position)
		return distance < self.radius + other_obj.radius + tolerance

	def collides_with_any(self, other_obj_list):
		colliders = False
		for obj in other_obj_list:
			distance = self.position.distance_to(obj.position)
			if distance < self.radius + obj.radius:
				colliders = True
		return colliders


class Ship(GameObject):
	MANEUVERABILITY = 10
	ACCELERATION = 0.5
	BULLET_SPEED = 5
	EXHAUST_INTERVAL = 100
	LASER_IMAGE = pg.image.load(f'{HOME_DIR}/laser_2.png').convert_alpha()
	LASER_IMAGE = pg.transform.rotate(LASER_IMAGE, 145)
	angle: float = -math.pi
	x: int = 1500
	y: int = 1500

	# def __init__(self, x=640, y=640, image=None):

	# 	self.visible = True
	def __init__(self, position, create_bullet_callback):
		self.create_bullet_callback = create_bullet_callback
		self.direction = Vector2(-math.pi)
		self.last = 0
		self.visible = False
		self.position = Vector2(Ship.x, Ship.y)
		self.x = Ship.x
		self.y = Ship.y
		self.image = SHIP
		self.angle = -math.pi
		self.speed = 0
		self.velocity = Vector2(0, 0)
		self.acceleration = Vector2(0, 0)
		self.max_speed = 10
		self.max_acceleration = 0.1
		self.rotation_speed = 0.1
		self.rotation_acceleration = 0.01
		self.rotation = 0
		self.rect = self.image.get_rect()
		self.rect.center = (self.x, self.y)
		super().__init__(position, SHIP, Vector2(0))

	def accelerate(self):
		now = pygame.time.get_ticks()
		if now > self.last + self.EXHAUST_INTERVAL:
			self.last = now
			x, y = Vector2(self.position) - self.velocity
			angle = int(self.position.angle_to(self.direction) - 52)
			pfx_module.add_stream(x, y, 10, (255, 0, 0), angle, 5, 2, 5, False, (255, 0, 0))
		self.velocity += self.direction * self.ACCELERATION

	def strafe_x(self, direction):
		self.x += direction * self.speed * 5

	def strafe_y(self, direction):
		self.y += direction * self.speed * 5

	def shine(self, screen):
		for i in range(120):
			px = (i * 131) % screen.get_width()
			py = int((math.sin(t + i * 0.27) * 0.5 + 0.5) * screen.get_height())
			c = (200 + (i * 3) % 55, 200 + (i * 5) % 55, 220 + (i * 7) % 35)
			if 0 <= px < screen.get_width() and 0 <= py < screen.get_height():
				screen.set_at((px, py), c)

	def rotate(self, clockwise=True):
		sign = 1 if clockwise else -1
		angle = self.MANEUVERABILITY * sign
		self.direction.rotate_ip(angle)

	def update(self):
		self.velocity += self.acceleration
		self.speed = self.velocity.length()
		self.x = math.pi * math.sin(angle := angle_to(self.x, self.y, mx, my))
		self.y = math.pi * math.cos(angle_to(self.x, self.y, mx, my))
		self.angle = angle
		self.rotation += self.rotation_acceleration
		self.rect.center = (self.x, self.y)

	def thrust(self, x, y):
		direction = Vector2(x - self.x, y - self.y).normalize()
		self.acceleration = direction * self.max_acceleration * self.angle
		self.rotation_acceleration = self.rotation_speed
		self.rotation_speed += 1.5

		PARTICLES.append(
			pfx_module.add_stream(self.image.get_rect().x,
			                      self.image.get_rect().y, 43, (255, 0, 0),
			                      random.randint(300, 360), 10, 4, 5, 0,
			                      secondcolor=(255, 255, 180)))

	def draw(self, surface):
		angle = self.direction.angle_to(Vector2(0, 1))
		rotated_surface = rotozoom(self.sprite, angle, 1.0)
		rotated_surface_size = Vector2(rotated_surface.get_size())
		blit_position = self.position - rotated_surface_size * 0.5
		surface.blit(rotated_surface, blit_position)

	def shoot(self):
		bullet_velocity = self.direction * self.BULLET_SPEED + self.velocity
		bullet = Bullet(self.position, bullet_velocity)
		self.create_bullet_callback(bullet)

	def rotate_image(self, image, angle):
		rot_image = pg.transform.rotate(image, angle)
		return rot_image, rot_image.get_rect(center=image.get_rect(topleft=(self.x, self.y)).center)

	def shoot_guns(self, ship_x, ship_y):
		STREAMS.append(pox_module.flash_screen(255, screen))
		BULLETS.append(Bullet(LASER_IMAGE, self.x // 2, self.y // 2, self.angle))
		STREAMS.append(
			pox_module.add_charge(ship_x + 300, ship_y + 300, int(random.randint(50, 60)), (255, 255, 0),
			                      gravity=False))


enterprise = Ship((1000, 1000), lambda bullet: BULLETS.append(bullet))
enterprise.draw(screen)
enterprise.shine(screen)


class Bullet(GameObject):
	def __init__(self, position, velocity):
		ang_delta = position.angle_to(enterprise.direction)
		super().__init__(position, pg.transform.rotate(LASER_IMAGE, -ang_delta), velocity)

	def move(self, surface):
		self.position = self.position + self.velocity


class Star:

	def __init__(self, x, y, size, color):
		self.x = x
		self.y = y
		self.size = size
		self.color = color
		self.surface = pg.Surface((size, size)).convert_alpha()
		pg.gfxdraw.filled_circle(self.surface, int(size // 2), int(size // 2), int(size // 2), color)

	def update(self):
		self.y += self.size / 1.2
		if self.y > screen.get_height():
			jig = STARS.index(self)
			STARS.pop(jig)

	def move(self, screen):
		self.y += self.size / 1.2

	def draw(self, screen):
		screen.blit(self.surface, (self.x, self.y))


def starfield(width, height, single=False):
	if single:
		i = random.randint(0, 1000) // 100
		if i % 2 == 0:
			STARS.append(star := Star(random.randint(0, width), -2, random.randint(2, 4),
			                          star_color := (255, 255, 255)))
	return STARS


def _get_game_objects():
	game_objects = [*pfx_module.stream, *STREAMS, *STARS, enterprise, *BULLETS]

	if enterprise and enterprise.visible:
		game_objects.append(enterprise)
	return game_objects


def length2(dx, dy):
	return dx * dx + dy * dy


# starfield(screen.get_width(), screen.get_height(), single=False)

while running:
	screen.fill((0, 0, 10))

	for event in pg.event.get():
		if event == QUIT:
			running = False
		if event == KEYDOWN and event.key == K_ESCAPE:
			running = False

	keys = pg.key.get_pressed()
	mx, my = pg.mouse.get_pos()

	if keys[K_j]:
		# SHIP = SHIP_L1
		# ANIMATIONS.append(SHIP_L1)
		# ANIMATIONS.append(SHIP_L2)
		# ANIMATIONS.append(SHIP_L3)
		ANIMATIONS.append(SHIP_L)
		ship_x -= 2

	if keys[K_i]:
		enterprise.thrust(math.sin(enterprise.angle) * enterprise.max_speed,
		                  math.cos(enterprise.angle) * enterprise.max_speed)
		PARTICLES.append(
			ship_particle := pfx_module.add_stream(enterprise.rect.x + enterprise.rect.x // 2,
			                                       enterprise.rect.y + enterprise.rect.y // 2, 30, (255, 180, 0),
			                                       180, 10, 12, 0.6))
		print(enterprise.rect.x, enterprise.rect, enterprise.x)
	if keys[K_l]:
		# SHIP = SHIP_R1
		# ANIMATIONS.append(SHIP_R1)
		# ANIMATIONS.append(SHIP_R2)
		# ANIMATIONS.append(SHIP_R3)
		ANIMATIONS.append(SHIP_R)
		ship_x += 2

	NOW_MS = 0
	keyinterval = 100
	laserinterval = 200
	keypress = pg.time.get_ticks()
	if enterprise and enterprise.visible:

		keys = pg.key.get_pressed()
		if NOW_MS > keypress + keyinterval:
			if keys[pg.K_w]:
				keypress = pg.time.get_ticks()
				enterprise.accelerate()
			if keys[pg.K_UP]:
				keypress = pg.time.get_ticks()
				enterprise.strafe_y(-2)
			if keys[pg.K_DOWN]:
				keypress = pg.time.get_ticks()
				enterprise.strafe_y(2)
			if keys[pg.K_a]:
				keypress = pg.time.get_ticks()
				enterprise.rotate(clockwise=False)
			if keys[pg.K_LEFT]:
				keypress = pg.time.get_ticks()
				enterprise.strafe_x = -2
			if keys[pg.K_d]:
				keypress = pg.time.get_ticks()
				enterprise.rotate(clockwise=True)
			if keys[pg.K_RIGHT]:
				keypress = pg.time.get_ticks()
				enterprise.strafe_x = 2
			if keys[pg.K_SPACE]:
				keypress = pg.time.get_ticks()
				laserkey += 1
				if laserkey > laserinterval:
					enterprise.shoot()
					laserkey = 0
	if keys[K_h]:
		enterprise.rotate_image(SHIP, enterprise.angle - 0.4)
	if keys[K_k]:
		enterprise.rotate_image(SHIP, enterprise.angle + 0.4)

	if keys[K_ESCAPE]:
		running = False

	if keys[K_SPACE]:
		enterprise.shine(screen)
		enterprise.shoot_guns(ship_x, ship_y)

	frame += 1
	if frame > len(ANIMATIONS):
		frame = 0
	enterprise.image = rotozoom(SHIP, angle_to(ship_x, ship_y, mx, my) * 100, ship_scale)
	enterprise.update()
	enterprise.draw(screen)
	try:
		for i in STREAMS:
			if hasattr(i, 'update'):
				i.update(screen)
			if hasattr(i, 'draw'):
				i.draw(screen)
			if not collide_circle(i, screen):
				STREAMS.remove(i)
		STREAMS.clear()
		for s in STARS:
			s.update()
			s.draw(screen)
			if s.y > screen.get_height():
				STARS.remove(s)
	except RuntimeError as e:
		print(f"ERROR occurred in {e}")
	starfield(screen.get_width(), screen.get_height(), single=True)

	if len(ANIMATIONS) > 1:
		ANIMATIONS.pop()
		if len(ANIMATIONS) == 1:
			ANIMATIONS.clear()
			ANIMATIONS = [SHIP]

	for b in pfx_module.stream:
		for p in pfx_module.spriteGroup:
			p.update(screen)
			screen.blit(p.image, (p.rect.x + 4000, p.rect.y + 4000))
	pfx_module.stream.clear()

	ANIMATIONS = [SHIP]
	for game_object in _get_game_objects():

		if isinstance(game_object, Star):
			continue
		if is_int(str(game_object)):
			del game_object
			continue
		if hasattr(game_object, 'rotate_in_place'):
			game_object.rotate_in_place()
		if hasattr(game_object, 'move'):
			game_object.move(screen)

		game_object.draw(screen)

	enterprise.shine(screen)
	screen.blit(render_char("DarkVoid2 beta 0.012", (100, 100, 255)), (10, 10))

	pg.display.flip()
	clock.tick(159)
