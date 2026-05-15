import sys
from idlelib.configdialog import is_int
import pygame as pg
from pygame.locals import *
import pygame.gfxdraw, random, math
from pygame.math import Vector2
from pygame.sprite import collide_rect, collide_circle
from pygame.transform import rotozoom
import pox_module, pfx_module
import poof_module
# import lvl_module
import hs_module
from typing import Tuple
from darkvoid2 import Ship, spawn_enemy

# import intro_module

HOME_DIR = "/home/shs/PycharmProjects/DarkVoid2"
pg.init()
font_size = 21
font = pygame.font.Font(f'{HOME_DIR}/assets/VL-Gothic-Regular.ttf', font_size)
pygame.display.set_icon(font.render("シ", True, (0, 255, 0)))
screen = pg.display.set_mode((2160, 1440), SRCALPHA)

STARS = []
ANIMATIONS = []
PARTICLES = []
STREAMS = []
BULLETS = []

SHIP = pg.image.load(f"{HOME_DIR}/assets/ship_neutral_2.png", "Ship neutral").convert_alpha()
SHIP_L1 = pg.image.load(f"{HOME_DIR}/assets/ship_left_1.png", "Ship left").convert_alpha()
SHIP_L2 = pg.image.load(f"{HOME_DIR}/assets/ship_left_2.png", "Ship left").convert_alpha()
SHIP_L3 = pg.image.load(f"{HOME_DIR}/assets/ship_left_3.png", "Ship left").convert_alpha()
SHIP_L = pg.image.load(f"{HOME_DIR}/assets/ship_left.png", "Ship left").convert_alpha()
SHIP_R1 = pg.image.load(f"{HOME_DIR}/assets/ship_right_1.png", "Ship right").convert_alpha()
SHIP_R2 = pg.image.load(f"{HOME_DIR}/assets/ship_right_2.png", "Ship right").convert_alpha()
SHIP_R3 = pg.image.load(f"{HOME_DIR}/assets/ship_right_3.png", "Ship right").convert_alpha()
SHIP_R = pg.image.load(f"{HOME_DIR}/assets/ship_right.png", "Ship right").convert_alpha()
LASER_IMAGE = pg.image.load(f'{HOME_DIR}/assets/laser_2.png', "Laser beam").convert_alpha()
LASER_IMAGE = pg.transform.rotate(LASER_IMAGE, 145)
running = True
clock = pg.time.Clock()
ship_x, ship_y = screen.get_width() // 2, screen.get_height() - SHIP.get_height() - 50

from enum import Enum


class State(Enum):
	""" The name of the game """
	INTRO = 0
	WAITINGFORUSER = 1
	PLAYING = 2
	DIED_WATCHING_ROCKS = 3
	WAITINGFORGAME = 4
	NEXTLEVEL = 5
	HIGHSCORETYPING = 6
	HIGHSCORES = 7


curr_state = State.INTRO


def angle_to(from_x, from_y, to_x, to_y):
	return math.atan2(to_y - from_y, to_x - from_x)


render_cache: dict[Tuple[int, int, int], pg.Surface] = {}
t = pg.time.get_ticks() * 0.001
ship_scale = 0.5
frame = 0


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


curr_state = State.WAITINGFORUSER


class Ship(GameObject):
	MANEUVERABILITY = 10
	ACCELERATION = 0.1
	BULLET_SPEED = 5
	EXHAUST_INTERVAL = 50
	LASER_IMAGE = pg.image.load(f'{HOME_DIR}/assets/laser_2.png').convert_alpha()
	LASER_IMAGE = pg.transform.rotate(LASER_IMAGE, 180)
	LASER2_IMAGE = pg.image.load(f'{HOME_DIR}/assets/laser.png').convert_alpha()
	LASER_IMAGE2 = pg.transform.rotate(LASER2_IMAGE, 180)
	angle: float = -math.pi
	x: int = 1500
	y: int = 1500

	# def __init__(self, x=640, y=640, image=None):

	def __init__(self, position, create_bullet_callback):
		self.create_bullet_callback = create_bullet_callback
		self.direction = Vector2(-math.pi)
		self.last = 0
		self.visible = False
		self.position = Vector2(Ship.x, Ship.y)
		self.x = Ship.x
		self.y = Ship.y
		self.image = SHIP
		self.angle = 0
		self.speed = 0
		self.velocity = Vector2(0, 0)
		self.acceleration = Vector2(0, 0)
		self.max_speed = 5
		self.max_acceleration = 0.05
		self.rotation_speed = 0.1
		self.rotation_acceleration = 0.01
		self.rotation = 0
		self.rect = self.image.get_rect()
		self.rect.center = (self.x, self.y)
		super().__init__(position, rotozoom(self.image, 0, 0.5), Vector2(0))

	def rotate(self, clockwise=True):
		sign = 1 if clockwise else -1
		angle = self.MANEUVERABILITY * sign
		self.direction.rotate_ip(angle)

	def accelerate(self):
		now = pygame.time.get_ticks()
		if now > self.last + self.EXHAUST_INTERVAL:
			self.last = now
			x, y = Vector2(self.position) - self.velocity
			angle = int(self.position.angle_to(self.direction) - 52)

		pfx_module.add_stream(self.position.x, self.position.y, 30, (255, 0, 0), angle, 5, 2, 5, False, (255, 255, 0))
		self.velocity += self.direction * self.ACCELERATION

	def strafe_x(self, direction):
		self.position.x += direction

	def strafe_y(self, direction):
		self.position.y += direction

	def shine(self, screen):
		for i in range(120):
			px = (i * 131) % screen.get_width()
			py = int((math.sin(t + i * 0.27) * 0.5 + 0.5) * screen.get_height())
			c = (200 + (i * 3) % 55, 200 + (i * 5) % 55, 220 + (i * 7) % 35)
			if 0 <= px < screen.get_width() and 0 <= py < screen.get_height():
				screen.set_at((px, py), c)

	def rotate(self, clockwise=True):
		now = pygame.time.get_ticks()
		sign = 1 if clockwise else -1
		angle = self.MANEUVERABILITY * sign
		self.direction.rotate_ip(angle)

	def update(self, mouse_x, mouse_y):
		now = pygame.time.get_ticks()
		self.velocity += self.acceleration
		self.speed = self.velocity.length()
		# Limit max speed
		if self.speed > self.max_speed:
			self.velocity = self.velocity.normalize() * self.max_speed
		# Update position with velocity
		self.position += self.velocity
		# Point ship nose toward mouse cursor
		self.angle = angle_to(self.position.x, self.position.y, mouse_x, mouse_y)

		self.direction = Vector2(math.cos(self.angle), math.sin(self.angle))
		self.rotation += self.rotation_acceleration
		self.rect.center = (self.position.x, self.position.y)

	def thrust(self, x, y):
		now = pygame.time.get_ticks()
		direction = Vector2(x - self.x, y - self.y).normalize()
		self.acceleration = direction * self.max_acceleration * self.angle
		self.rotation_acceleration = self.rotation_speed
		self.rotation_speed += 1.5

		PARTICLES.append(
			pfx_module.add_stream(self.position.x,
			                      self.position.y + 50, 43, (255, 0, 0),
			                      random.randint(300, 360), 10, 4, 5, 0,
			                      secondcolor=(255, 255, 180)))

	def draw(self, surface):
		# angle = self.direction.angle_to(Vector2(0, 1))
		angle = self.direction.angle_to(Vector2(0, 1))
		rotated_surface = rotozoom(self.sprite, angle, 0.3)
		rotated_surface_size = Vector2(rotated_surface.get_size())
		blit_position = self.position - rotated_surface_size * 0.5
		surface.blit(rotated_surface, blit_position)

	def shoot(self):
		STREAMS.append(pox_module.flash_screen(255, screen))
		bullet_velocity = self.direction * self.BULLET_SPEED + self.velocity
		bullet = Bullet(self.position, bullet_velocity)
		BULLETS.append(bullet)
		self.create_bullet_callback(bullet)

	def shoot_guns(self, ship_x, ship_y):
		# pg.mixer.Sound.play(pg.mixer.Sound(f'{HOME_DIR}/assets/lasersound.wav'))
		STREAMS.append(pox_module.flash_screen(255, screen))
		bullet_velocity = self.direction * self.BULLET_SPEED + self.velocity
		bullet = Bullet(self.position, bullet_velocity)
		BULLETS.append(bullet)
		STREAMS.append(pox_module.add_charge(ship_x + 300, ship_y + 300, int(random.randint(10, 30)), (255, 255, 0),
		                                     gravity=False))
		self.create_bullet_callback(bullet)

	def rotate_image(self, image, angle):
		rot_image = pg.transform.rotate(image, angle)
		return rot_image, rot_image.get_rect(center=image.get_rect(topleft=(self.position.x, self.position.y)).center)

	enterprise = Ship((1280, 1024), lambda bullet: BULLETS.append(bullet))

	enterprise.draw(screen)
	enterprise.shine(screen)


def wrap_position(position, surface):
	x, y = position
	w, h = surface.get_size()
	return Vector2(x % (w + enterprise.image.get_width()), y % (h + enterprise.image.get_height()))


class Bullet(GameObject):
	def __init__(self, position, velocity):
		ang_delta = position.angle_to(enterprise.direction)
		super().__init__(position, pg.transform.rotate(LASER_IMAGE, -ang_delta), -velocity)
		pg.mixer.Sound.play(pg.mixer.Sound(f'{HOME_DIR}/assets/lasersound.wav'))

	def move(self, surface):
		self.position = self.position + self.velocity


class Star:

	def __init__(self, x, y, size, color):
		self.x = x
		self.y = y
		self.size = size
		self.color = color
		self.surface = pg.Surface((size, size)).convert_alpha()
		pg.gfxdraw.filled_circle(self.surface, int(size // 3), int(size // 3), int(size // 3), color)

	def update(self):
		self.y += self.size / 1.3
		if self.y > screen.get_height():
			jig = STARS.index(self)
			STARS.pop(jig)

	def move(self, screen):
		self.y += self.size / 1.5

	def draw(self, screen):
		screen.blit(self.surface, (self.x, self.y))


curr_state = State.WAITINFORGAME
ASTEROID_COUNT = 5
MAX_ASTEROIDS = 10
MIN_ASTEROID_DISTANCE = 200
asteroids = []
ROCK1 = pygame.image.load(f'{HOME_DIR}/assets/rock_3_2.png').convert_alpha()
ROCK2 = pygame.image.load(f'{HOME_DIR}/assets/rock_4_2.png').convert_alpha()
ROCK3 = pygame.image.load(f'{HOME_DIR}/assets/rock_5_2.png').convert_alpha()
ROCK4 = pygame.image.load(f'{HOME_DIR}/assets/rock_6_2.png').convert_alpha()
BACKGROUND = pygame.image.load(f'{HOME_DIR}/assets/01362_overtime_1920x1080').convert_alpha()
ROCK_IMAGES = [ROCK1, ROCK2, ROCK3, ROCK4]

for a in range(ASTEROID_COUNT):
	asteroids.append(spawn_enemy(a))


class Asteroid(GameObject):
	def __init__(self, position, create_asteroid_callback, size=4):
		self.create_asteroid_callback = create_asteroid_callback
		self.size = size
		self.hp = size * level.asteroid_hp
		self.hit = False
		self.rotation = 0
		size_to_scale = {5: 0.7, 4: 0.6, 3: 0.5, 2: 0.4, 1: 0.3}
		self.scale = size_to_scale[size]
		self.ASTEROID_IMAGE = random.choice(ROCK_IMAGES)
		self.sprite = rotozoom(self.ASTEROID_IMAGE, 0, self.scale).convert_alpha()
		self.rotdelta = random.randint(-100, 100) / 100
		super().__init__(position, self.sprite, get_random_velocity(2, 10) / 8 * level.asteroid_speed)

	def draw(self, surface):
		if self.hit:
			blit_position = self.position - Vector2(self.radius)
			self.sprite.fill((255, 255, 255, 255), None, pygame.BLEND_ADD)
			surface.blit(self.sprite, blit_position)
			self.hit -= 1
		else:
			blit_position = self.position - Vector2(self.radius)
			surface.blit(self.sprite, blit_position)

	def rotate_in_place(self):
		self.rotated_image = pygame.transform.rotate(rotozoom(self.ASTEROID_IMAGE, 0, self.scale), self.rotation)
		self.rotation += self.rotdelta
		self.sprite = self.rotated_image
		self.radius = self.sprite.get_width() / 2

		def create_asteroid_callback(asteroid):
			asteroid.create_asteroid_callback(asteroid)


def spawn_enemy(amount, new=False):
	if amount > MAX_ASTEROIDS:
		amount = MAX_ASTEROIDS
	while len(asteroids) < amount or new:
		for _ in range(amount):
			while True:
				position = get_random_position(screen)

				if new:
					print(f"new on {position}")
					position = Vector2(-100, -100)
					new = False

				if (
						position.distance_to(ship.position)
						> MIN_ASTEROID_DISTANCE
				):
					break

			asteroids.append(Asteroid(position, asteroids.append, random.randint(1, 5)))

		if len(asteroids) > 0:
			for a in asteroids:
				for c in range(0, len(asteroids)):
					if a == asteroids[c]:
						continue
					if a.position.distance_to(asteroids[c].position) < MIN_ASTEROID_DISTANCE:
						del asteroids[c]
						break


laserinterval = 3
laserkey = 0
keyinterval = 50
keypress = 0
message = ""
blastinterval = 1000
last = 0


def add_one_charge(x, y, amount, last):
	now = pygame.time.get_ticks()
	if now > last + blastinterval:
		pox_module.add_charge(x, y, amount, (255, 255, 255), False)
		last = now
	return last


def starfield(width, height, single=False):
	if single:
		i = random.randint(0, 1000) // 100
		if i % 3 == 0:
			STARS.append(star := Star(random.randint(0, width), -2, random.randint(2, 4),
			                          star_color := (255, 255, 255)))
	return STARS


def _get_game_objects():
	game_objects = [*pfx_module.stream, *STREAMS, *STARS, enterprise, *ASTEROIDS, *BULLETS]

	if enterprise and enterprise.visible:
		game_objects.append(enterprise)
	return game_objects


def length2(dx, dy):
	return dx * dx + dy * dy


# One last bang amd starry skies
add_one_charge(screen.get_width() // 2, screen.get_height() // 2, 500, 0)
starfield(screen.get_width(), screen.get_height(), single=False)
laserkey = 0

while running:
	screen.fill((0, 0, 10))
	screen.blit(BACKGROUND, (0, 0))

	for event in pg.event.get():
		if event == QUIT:
			running = False
		if event == KEYDOWN and event.key == K_ESCAPE:
			running = False

	keys = pg.key.get_pressed()
	mx, my = pg.mouse.get_pos()

if keys[K_ESCAPE]:
	running = False

if keys[K_j]:
	ANIMATIONS.append(SHIP_L)
	ship_x -= 2

if keys[K_q]:
	running = False

if keys[K_i]:
	enterprise.thrust(math.sin(enterprise.angle) * enterprise.max_speed,
	                  math.cos(enterprise.angle) * enterprise.max_speed)
	PARTICLES.append(
		ship_particle := pfx_module.add_stream(enterprise.position.x,
		                                       enterprise.position.y, 30, (255, 180, 0),
		                                       180, 10, 12, 0.6))

if keys[K_l]:
	ANIMATIONS.append(SHIP_R)
	ship_x += 2

# WASD and Arrow key controls
# W key: accelerate forward
if keys[pg.K_w]:
	enterprise.accelerate()
# A key: strafe left
if keys[pg.K_a]:
	enterprise.strafe_x(-3)
# S key: accelerate backward
if keys[pg.K_s]:
	enterprise.velocity -= enterprise.direction * enterprise.ACCELERATION * 0.5
# D key: strafe right
if keys[pg.K_d]:
	enterprise.strafe_x(3)

# Arrow key controls
if keys[pg.K_UP]:
	enterprise.accelerate()
if keys[pg.K_DOWN]:
	velocity = enterprise.velocity.length()
enterprise.velocity = enterprise.direction * (velocity - enterprise.ACCELERATION)
if keys[pg.K_LEFT]:
	enterprise.rotate(clockwise=False)
if keys[pg.K_RIGHT]:
	enterprise.rotate(clockwise=True)

if keys[K_SPACE]:
	enterprise.shine(screen)
	laserkey += 1
	if laserkey > 500:
		enterprise.shoot()
		pg.mixer.Sound.play(pg.mixer.Sound(f'{HOME_DIR}/assets/lasersound.wav'))
		laserkey = 0

frame += 1
if frame > len(ANIMATIONS):
	frame = 0

enterprise.update(mx, my)
enterprise.draw(screen)

try:
	for i in STREAMS:
		if hasattr(i, 'update'):
			i.update(screen)
		if hasattr(i, 'draw'):
			i.draw(screen)
	STREAMS.clear()
	for s in STARS:
		s.update()
		s.draw(screen)
		if s.y > screen.get_height():
			if s in STARS:
				STARS.remove(s)
except RuntimeError as e:
	print(f"ERROR occurred in {e}")

starfield(screen.get_width(), screen.get_height(), single=True)

if len(ANIMATIONS) > 1:
	ANIMATIONS.pop()
	if len(ANIMATIONS) == 1:
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
	screen.blit(render_char("DarkVoid2 beta 0.01221", (100, 100, 255)), (10, 10))

	pg.display.flip()
	clock.tick(159)

pg.quit()
pg.mixer.quit()
sys.exit()
