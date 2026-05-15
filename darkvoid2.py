from idlelib.configdialog import is_int
import pygame as pg
from pygame.locals import *
# from PIL import Image, ImageDraw
import pygame.gfxdraw, random, math
from pygame.math import Vector2
from pygame.sprite import collide_rect, collide_circle
from pygame.transform import rotozoom
import pox_module, pfx_module
import poof_module
import intro_module
# import hs_module
from typing import Tuple
import pygame.mixer

HOME_DIR = "/home/shs/PycharmProjects/DarkVoid2"
pg.init()

screen = pg.display.set_mode((2000, 1500), SRCALPHA)


class Level:
	def __init__(self):
		self.stage = 1
		self.asteroids = 7
		self.asteroid_speed = 1
		self.asteroid_hp = 1

	def up(self):
		self.stage += 1
		self.asteroids += 1
		self.asteroid_speed += 0.20
		self.asteroid_hp += 0.20


level = Level()

msg_font = pygame.font.SysFont('msgothic', 36)


def zoom_text(msg, color, opacity, rot=1.00, sca=4.00, zoomfont=msg_font):
	fs = zoomfont.render(msg, True, color)
	rotated = pygame.transform.rotozoom(fs, rot, sca)
	sca -= 0.05
	rotated.set_alpha(opacity)
	xd = rotated.get_width()
	yd = rotated.get_height()
	screen.blit(rotated, (screen.get_width() / 2 - xd / 2, screen.get_height() / 2 - yd / 2))


# intro_module.intro(screen)
STARS = []
ANIMATIONS = []
PARTICLES = []
STREAMS = []
BULLETS = []
ASTEROIDS = []
SHIP = pg.image.load(f"{HOME_DIR}/assets/ship_neutral_2.png", "Ship neutral").convert_alpha()
SHIP_L1 = pg.image.load(f"{HOME_DIR}/assets/ship_left_1.png", "Ship left").convert_alpha()
SHIP_L2 = pg.image.load(f"{HOME_DIR}/assets/ship_left_2.png", "Ship left").convert_alpha()
SHIP_L3 = pg.image.load(f"{HOME_DIR}/assets/ship_left_3.png", "Ship left").convert_alpha()
SHIP_L = pg.image.load(f"{HOME_DIR}/assets/ship_left.png", "Ship left").convert_alpha()
SHIP_R1 = pg.image.load(f"{HOME_DIR}/assets/ship_right_1.png", "Ship right").convert_alpha()
SHIP_R2 = pg.image.load(f"{HOME_DIR}/assets/ship_right_2.png", "Ship right").convert_alpha()
SHIP_R3 = pg.image.load(f"{HOME_DIR}/assets/ship_right_3.png", "Ship right").convert_alpha()
SHIP_R = pg.image.load(f"{HOME_DIR}/assets/ship_right.png", "Ship right").convert_alpha()
LASER_IMAGE = pg.image.load(f'/home/shs/PycharmProjects/DarkVoid2/assets/laser.png', "Laser beam").convert_alpha()
LASER_IMAGE = pg.transform.rotate(LASER_IMAGE, 145)
running = True
clock = pg.time.Clock()
ship_x, ship_y = screen.get_width() // 2, screen.get_height() - SHIP.get_height() - 50

if level == 1:
	pygame.mixer.music.load(f'{HOME_DIR}/assets/Ov Moi Omm - The Dictator’s Transmission (YSMHB).mp3')
	pygame.mixer.init(48000, -16, 2, 4096)
	pygame.mixer.music.play(-1)
	pygame.mixer.music.set_volume(0.2)
if level == 2:
	pygame.mixer.music.load(f'{HOME_DIR}/assets/Jahzzar - Forest Pan.mp3')
	pygame.mixer.init(48000, -16, 2, 4096)
	pygame.mixer.music.play(-1)
	pygame.mixer.music.set_volume(0.2)
zoom_text("DARK VOID 2", (255, 255, 255), 255, rot=0.00, sca=4.0)

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


def get_random_position(surface):
	return Vector2(
		random.randrange(surface.get_width()),
		random.randrange(surface.get_height()),
	)


def get_random_velocity(min_speed, max_speed):
	speed = random.randint(min_speed, max_speed)
	angle = random.randrange(0, 360)
	return Vector2(speed, 0).rotate(angle)


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
			if not hasattr(obj, 'position'):
				continue
			distance = self.position.distance_to(obj.position)
			if distance < self.radius + obj.radius:
				colliders = True
		return colliders


class Ship(GameObject):
	MANEUVERABILITY = 8
	ACCELERATION = 0.01
	BULLET_SPEED = 2
	EXHAUST_INTERVAL = 50
	LASER_IMAGE = pg.image.load(f'{HOME_DIR}/assets/laser_2.png').convert_alpha()
	LASER_IMAGE = pg.transform.rotate(LASER_IMAGE, 180)
	LASER_IMAGE2 = pg.image.load(f'{HOME_DIR}/assets/laser.png').convert_alpha()
	LASER_IMAGE2 = pg.transform.rotate(LASER_IMAGE2, 0)
	angle: float = -Vector2(0, -1).angle_to(Vector2(0, -1))
	x: int = 1500
	y: int = 1500

	def __init__(self, position, create_bullet_callback):
		self.create_bullet_callback = create_bullet_callback
		self.direction = Vector2(0, -1)
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
		super().__init__(position, rotozoom(self.image, 0, 0.4), -Vector2(0))

	def accelerate(self):
		now = pygame.time.get_ticks()
		if now > self.last + self.EXHAUST_INTERVAL:
			self.last = now
			self.x, self.y = Vector2(self.position) - self.velocity
			angle = int(self.position.angle_to(self.direction) - 52)
			pfx_module.add_stream(self.x, self.y + 50, 30, (255, 0, 0), angle, 5, 2, 5, False,
			                      (255, 255, 0))
			self.velocity += self.direction * self.ACCELERATION

	def strafe_x(self, direction):
		self.position.x += direction

	def strafe_y(self, direction):
		self.position.y += direction

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
			pfx_module.add_stream(self.x, self.y + 50, 300, (255, 0, 0), random.randint(300, 360), 10, 4, 5, 0, ))

	def draw(self, surface):
		angle = self.direction.angle_to(Vector2(0, 1))
		rotated_surface = rotozoom(self.sprite, angle, 0.4)
		rotated_surface_size = Vector2(rotated_surface.get_size())
		blit_position = self.position - rotated_surface_size * 0.5
		surface.blit(rotated_surface, blit_position)

	def shoot(self):
		pg.mixer.Sound(f'{HOME_DIR}/assets/lasersound.wav').play()
		STREAMS.append(pox_module.flash_screen(255, screen))
		bullet_velocity = self.direction * self.BULLET_SPEED + self.velocity
		bullet = Bullet(self.position, bullet_velocity)
		BULLETS.append(bullet)
		self.create_bullet_callback(bullet)

	def rotate_image(self, image, angle):
		rot_image = pg.transform.rotate(image, angle)
		return rot_image, rot_image.get_rect(center=image.get_rect(topleft=(self.position.x, self.position.y)).center)

	def shoot_guns(self, ship_x, ship_y):
		STREAMS.append(pox_module.flash_screen(255, screen))
		pygame.mixer.Sound(f'{HOME_DIR}/assets/lasersound.wav').play()
		bullet_velocity = self.direction * self.BULLET_SPEED + self.velocity
		bullet = Bullet(self.position, bullet_velocity)
		BULLETS.append(bullet)
		# STREAMS.append(pox_module.add_charge(ship_x + 300, ship_y + 300, int(random.randint(10, 30)), (255, 255, 0),
		#                                   gravity=False))
		self.create_bullet_callback(bullet)


enterprise = Ship((1920, 1080), lambda bullet: BULLETS.append(bullet))

enterprise.rotate_image(SHIP, 0)
enterprise.draw(screen)

ASTEROID_COUNT = 5
MAX_ASTEROIDS = 10
MIN_ASTEROID_DISTANCE = 200
asteroids = []


def spawn_enemy(amount, new=True):
	MAX_ASTEROIDS = [amount in range(random.randint(1, 10))]

	while len(asteroids) < len(MAX_ASTEROIDS):
		for amount in range(ASTEROID_COUNT):
			while True:
				position = get_random_position(screen)

				if new:
					print(f"new on {position}")
					position = Vector2(-100, -100)
					new = False

				if (
						position.distance_to(enterprise.position)
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


key = pg.key.get_pressed()
if key[K_KP_MINUS]:
	spawn_enemy(1, new=True)

add_one_charge(ship_x + 300, ship_y + 300, int(random.randint(10, 300)), last)


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
		for x in range(1, 10):
			self.rotated_image = pygame.transform.rotate(rotozoom(self.ASTEROID_IMAGE, x, x // 2), self.rotation)
			self.rotation += self.rotdelta
			self.sprite = self.rotated_image
			self.radius = self.sprite.get_width() / 2


curr_state = State.WAITINGFORGAME
ASTEROID_COUNT = 2
MAX_ASTEROIDS = 5
MIN_ASTEROID_DISTANCE = 200
ASTEROIDS = []
ROCK1 = pygame.image.load(f'{HOME_DIR}/assets/rock_3_2.png').convert_alpha()
ROCK2 = pygame.image.load(f'{HOME_DIR}/assets/rock_4_2.png').convert_alpha()
ROCK3 = pygame.image.load(f'{HOME_DIR}/assets/rock_5_2.png').convert_alpha()
ROCK4 = pygame.image.load(f'{HOME_DIR}/assets/rock_6_2.png').convert_alpha()
BACKGROUND = pygame.image.load(f'{HOME_DIR}/assets/01362_overtime_1920x1080.jpg').convert_alpha()
ROCK_IMAGES = [ROCK1, ROCK2, ROCK3, ROCK4]


def asteroidium(level_instance):
	for _ in range(level_instance.asteroids):
		ASTEROIDS.append(Asteroid(get_random_position(
			pg.Surface((screen.get_width() * 4, screen.get_height() * 4))),
			asteroids.append, random.randint(1, 5)))


for a, b in ASTEROIDS:
	if a.collidewith(enterprise) or a.collidewith(*BULLETS) or a.collidewith(*ASTEROIDS):
		pg.mixer.Sound(f'{HOME}/assets/boom.wav').play()
	if b.collidewith(enterprise) or b.collidewith(*BULLETS) or b.collidewith(*ASTEROIDS):
		pg.mixer.Sound(f'{HOME}/assets/boom2.wav').play()
		if i := random.random() / 2 <= 0.5 and b.collidewith(*ASTEROIDS):
			pg.mixer.Sound(f'{HOME}/assets/boom5.wav').play()

asteroidium(level)


class Bullet(GameObject):
	def __init__(self, position, velocity):
		ang_delta = position.angle_to((mx, my))
		super().__init__(position, pg.transform.rotate(LASER_IMAGE, -ang_delta), -velocity)

	def move(self, surface):
		self.position = self.position + self.velocity


curr_state = State.PLAYING


class Star:

	def __init__(self, x, y, size, color):
		self.x = x
		self.y = y
		self.size = size
		self.color = color
		self.surface = pg.Surface((size, size)).convert_alpha()
		pg.gfxdraw.filled_circle(self.surface, int(size // 4), int(size // 4), int(size // 4), color)

	def update(self):
		self.y += self.size / 1.3
		if self.y > screen.get_height():
			jig = STARS.index(self)
			STARS.pop(jig)

	def move(self, screen):
		self.y += self.size / 1.5

	def draw(self, screen):
		screen.blit(self.surface, (self.x, self.y))


def _get_game_objects():
	game_objects = [*poof_module.spriteGroup, *pox_module.spriteGroup, *pfx_module.spriteGroup, *STREAMS, *ASTEROIDS,
	                *STARS,
	                enterprise, *BULLETS]
	if enterprise and enterprise.visible:
		game_objects.append(enterprise)
	return game_objects


def length2(dx, dy):
	return dx * dx + dy * dy


# starfield(screen.get_width(), screen.get_height(), single=False)
laserkey = 0
SCORE = 0

while running:
	screen.fill((0, 0, 10))
	# screen.blit(BACKGROUND, (0, 0))

	for event in pg.event.get():
		if event == QUIT:
			running = False
		if event == KEYDOWN and event.key == K_ESCAPE:
			running = False
		if event == MOUSEBUTTONDOWN and event.key == 1:
			pg.mixer.Sound(f'{HOME_DIR}/assets/lasersound').play()
			enterprise.shoot_guns(ship_x, ship_y)
			poof_module.add_smoke(enterprise.position.x + enterprise.x, enterprise.position.y + enterprise.y, 1000,
			                      (255, 180, 150))

	keys = pg.key.get_pressed()
	mx, my = pg.mouse.get_pos()

	if keys[K_j]:
		ANIMATIONS.append(SHIP_L)
		ship_x -= 2

	if keys[K_RETURN]:
		pg.mixer.Sound(f'{HOME_DIR}/assets/lasersound.wav').play()
		enterprise.shoot_guns(ship_x, ship_y)
		poof_module.add_smoke(enterprise.position.x + enterprise.x, enterprise.position.y + enterprise.y, 100)
	if keys[K_i]:
		enterprise.thrust(math.sin(enterprise.angle) * math.pi * 5,
		                  math.cos(enterprise.angle) * math.pi * 5)
		PARTICLES.append(
			ship_particle := pfx_module.add_stream(700, 700,
			                                       90, (255, 180, 0),
			                                       180, 10, 12, 0.6))

	if keys[K_l]:
		ANIMATIONS.append(SHIP_R)
		ship_x += 2

	if keys[pg.K_w]:
		enterprise.velocity -= enterprise.direction * enterprise.ACCELERATION
	if keys[pg.K_a]:
		enterprise.strafe_x(-2)
	if keys[pg.K_s]:
		enterprise.thrust = 0
		enterprise.velocity = 0
		enterprise.velocity += enterprise.direction * enterprise.ACCELERATION * 0.2
	if keys[pg.K_d]:
		enterprise.strafe_x(2)

	NOW_MS = 0
	keys = pygame.key.get_pressed()
	if NOW_MS > keypress + keyinterval:
		if keys[pygame.K_UP]:
			keypress = pygame.time.get_ticks()
			# enterprise.accelerate()
			enterprise.strafe_x(2)
		if keys[pygame.K_DOWN]:
			keypress = pygame.time.get_ticks()
			enterprise.strafe_x(-2)
		if keys[pygame.K_LEFT]:
			keypress = pygame.time.get_ticks()
			enterprise.rotate(clockwise=False)
		if keys[pygame.K_RIGHT]:
			keypress = pygame.time.get_ticks()
			enterprise.rotate(clockwise=True)
		if keys[pygame.K_SPACE]:
			keypress = pygame.time.get_ticks()
			laserkey += 1
			if laserkey > laserinterval:
				pygame.mixer.Sound(f'{HOME_DIR}/assets/lasersound.wav').play()
				enterprise.shoot_guns(ship_x, ship_y)
				poof_module.add_smoke(enterprise.position.x + enterprise.x, enterprise.position.y + enterprise.y, 100)
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

	collidetime = pygame.time.get_ticks()
	collision_delay = 150
	now = pygame.time.get_ticks()
	if now > collidetime + collision_delay:
		for rock in asteroids:
			if rock.collides_with_tolerance(asteroid, -15):
				temp = asteroid.velocity
				asteroid.velocity = rock.velocity
				asteroid.rotdelta = -asteroid.rotdelta
				asteroid.position = wrap_position(asteroid.position + asteroid.velocity * 2, screen)
				rock.velocity = temp
				rock.position = wrap_position(rock.position + rock.velocity * 2, screen)
				collidetime = pygame.time.get_ticks()
				break

	for bullet in BULLETS[:]:
		for asteroid in ASTEROIDS[:]:
			if asteroid.collides_with(bullet):
				asteroid.hp -= 1
				BULLETS.remove(bullet)
				asteroid.hit = 5
				if asteroid.hp < 1:
					SCORE += 1
					pox_module.add_charge(asteroid.position[0], asteroid.position[1], 300 * asteroid.size, (255, 0, 0),
					                      False)
					ASTEROIDS.remove(asteroid)
				break

	for bullet in BULLETS[:]:
		if not screen.get_rect().collidepoint(bullet.position):
			BULLETS.remove(bullet)

	if not enterprise and message == "YOU DIED":
		State = State.DIED_WATCHING_ROCKS
		once = True
		pygame.event.clear()
		pygame.event.post(pygame.event.Event(DIED))

	if not asteroids and enterprise and enterprise.visible:
		if once:
			lvl_timer = pygame.time.get_ticks()
		once = False
		message = "ENEMIES FELLED"
		msg_opacity = 255
		msg_rot = 1
		msg_sca = 1
		now = pygame.time.get_ticks()
		if now > lvl_timer + 2000:
			message = ""
			once = True
			enterprise.visible = False
			level.up()
			pygame.event.clear()
			pygame.event.post(pygame.event.Event(LEVELCHANGE))
	if len(ANIMATIONS) > 1:
		ANIMATIONS.pop()
		if len(ANIMATIONS) == 1:
			ANIMATIONS = [SHIP]

	ANIMATIONS = [SHIP]
	for game_object in _get_game_objects():

		if game_object is None:
			del game_object
			continue
		if is_int(int(str(game_object))):
			del game_object
			continue
		if hasattr(game_object, 'rotate_in_place'):
			game_object.rotate_in_place()
		if hasattr(game_object, 'move'):
			game_object.move(screen)
		if not hasattr(game_object, 'position'):
			screen.blit(game_object.image, game_object.rect)
			# for i in pox_module.spriteGroup:
			#	screen.blit(i.image, i.rect)
			# for i in poof_module.spriteGroup:
			# 		screen.blit(i.image, i.rect)
			# 	for i in pfx_module.spriteGroup:
			#		screen.blit(i.image, i.rect)

			game_object.draw(screen)

	screen.blit(render_char("DarkVoid2 beta 0.014", (100, 100, 255)), (10, 10))

	pg.display.flip()
	clock.tick(159)

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

	for b in pfx_module.stream:
		for p in pfx_module.spriteGroup:
			p.update(screen)
			screen.blit(p.image, (p.rect.x + enterprise.x, p.rect.y + enterprise.y + 500))
	# pfx_module.stream.clear()

	ANIMATIONS = [SHIP]
	for game_object in _get_game_objects():
		if not hasattr(game_object, 'position'):
			continue
		if game_object.collides_with_any(game_object2 := _get_game_objects()):
			if isinstance(game_object2, Asteroid):
				game_object2.velocity = -game_object2.velocity
				game_object.velocity = -game_object.velocity
				game_object.radius = game_object.sprite.get_width() / 2
				game_object2.radius = game_object2.sprite.get_width() / 2
				game_object.hp -= 1
				game_object2.hp -= 1

		if isinstance(game_object, Asteroid):
			game_object.hit = 100
		if game_object.collides_with_any(BULLETS):
			if isinstance(game_object, Asteroid):
				game_object.hp -= 1
				game_object.radius = game_object.sprite.get_width() / 2
				try:
					if game_object.hp <= 0:
						asteroids.remove(game_object)
					if game_object not in ASTEROIDS:
						ASTEROIDS.remove(game_object)
				except ValueError as e:
					print(f"{game_object}")
				add_one_charge(game_object.position.x, game_object.position.y, int(random.randint(10, 300)), last)

		if isinstance(game_object, Star):
			continue
		if game_object is None:
			del game_object
			continue
		if is_int(str(game_object)):
			del game_object
			continue
		if hasattr(game_object, 'rotate_in_place'):
			game_object.rotate_in_place()
		if hasattr(game_object, 'move'):
			game_object.move(screen)

		if not hasattr(game_object, 'sprite'):
			continue
		screen.blit(game_object.sprite, game_object.position)

pygame.quit()
pygame.mixer.fadeout(2000)
pygame.mixer.stop()
