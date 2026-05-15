from sprite_anim import draw_left, draw_right
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
# import intro_module
import hs_module
from typing import Tuple
import pygame.mixer
import os


# intro_module.LOGOEVENT = pg.USEREVENT + 1
# intro_module.FADEOUTEVENT = pg.USEREVENT + 2
#
# intro_module.INITEVENT = pg.USEREVENT + 3
# intro_module.INITGAME = pg.USEREVENT + 4


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


import commons as c

level = Level()


def zoom_text(msg, color, opacity, rot=1.00, sca=4.00, zoomfont=c.msg_font):
	fs = zoomfont.render(msg, True, color)
	rotated = pygame.transform.rotozoom(fs, rot, sca)
	sca -= 0.05
	rotated.set_alpha(opacity)
	xd = rotated.get_width()
	yd = rotated.get_height()
	c.screen.blit(rotated, (c.screen.get_width() / 2 - xd / 2, c.screen.get_height() / 2 - yd / 2))


c.running = True
c.clock = pg.time.Clock()

if level.stage == 2:
	pygame.mixer.music.load(f'{c.HOME_DIR}/assets/Jahzzar - Forest Pan.mp3')
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
	ACCELERATION = 0.5
	BULLET_SPEED = 2
	EXHAUST_INTERVAL = 50
	LASER_IMAGE2 = pg.image.load(f'{c.HOME_DIR}/assets/laser_2.png').convert_alpha()
	LASER_IMAGE2 = pg.transform.rotate(LASER_IMAGE2, 180)
	LASER_IMAGE = pg.image.load(f'{c.HOME_DIR}/assets/laser.png').convert_alpha()
	LASER_IMAGE = pg.transform.rotate(LASER_IMAGE, 0)
	angle: float = Vector2(0, 0)
	x: int = 1920 // 2
	y: int = 800

	def __init__(self, position, create_bullet_callback):
		self.create_bullet_callback = create_bullet_callback
		self.direction = Vector2(1, 0)
		self.last = 0
		self.visible = True
		self.position = Vector2(Ship.x, Ship.y)
		self.x = Ship.x
		self.y = Ship.y
		self.image = c.SHIP
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
		c.now = pg.time.get_ticks()
		if c.now > self.last + self.EXHAUST_INTERVAL:
			self.last = c.now
			self.x, self.y = Vector2(self.position) - self.velocity
			angle = int(self.position.angle_to(self.direction) - 52)
			c.STREAMS.append(pfx_module.add_stream(self.x, self.y + 50, 30, (255, 0, 0), angle, 5, 2, 5, False,
			                                       (255, 255, 0)))
			self.velocity += self.direction * self.ACCELERATION

	def strafe_x(self, direction):
		new_x = self.position.x + direction
		# Clamp to screen bounds
		if 0 < new_x < c.screen.get_width():
			self.position.x = new_x

	def strafe_y(self, direction):
		new_y = self.position.y + direction
		# Clamp to screen bounds
		if 0 < new_y < c.screen.get_height():
			self.position.y = new_y

	def update(self):
		c.now = pg.time.get_ticks()
		self.velocity += self.acceleration
		self.speed = self.velocity.length()
		# Limit max speed
		if self.speed > self.max_speed:
			self.velocity = self.velocity.normalize() * self.max_speed
		# Update position with velocity
		self.position += self.velocity
		self.direction = Vector2(math.cos(self.angle), math.sin(self.angle))
		self.rotation += self.rotation_acceleration
		self.rect.center = (self.position.x, self.position.y)

	def thrust(self, x, y):
		c.now = pygame.time.get_ticks()
		direction = Vector2(x - self.x, y - self.y).normalize()
		self.acceleration = direction * self.max_acceleration * self.angle
		self.rotation_acceleration = self.rotation_speed
		self.rotation_speed += 1.5

		c.STREAMS.append(
			pfx_module.add_stream(self.x, self.y + 50, 300, (255, 0, 0), random.randint(300, 360), 10, 4, 5, 0, ))

	def draw(self, surface):
		angle = self.direction.angle_to(Vector2(0, 1))
		rotated_surface = rotozoom(self.sprite, angle, 0.4)
		rotated_surface_size = Vector2(rotated_surface.get_size())
		blit_position = self.position - rotated_surface_size * 0.5
		surface.blit(rotated_surface, blit_position)

	def shoot(self):
		pg.mixer.Sound(f'{c.HOME_DIR}/assets/lasersound.wav').play()
		c.STREAMS.append(pox_module.flash_screen(255, c.screen))
		bullet_velocity = self.direction * self.BULLET_SPEED + self.velocity
		bullet = Bullet(self.position, bullet_velocity)
		c.BULLETS.append(bullet)
		self.create_bullet_callback(bullet)

	def rotate_image(self, image, angle):
		rot_image = pg.transform.rotate(image, angle)
		return rot_image, rot_image.get_rect(center=image.get_rect(topleft=(self.position.x, self.position.y)).center)

	def shoot_guns(self, ship_x, ship_y):
		c.STREAMS.append(pox_module.flash_screen(255, c.screen))
		pygame.mixer.Sound(f'{c.HOME_DIR}/assets/lasersound.wav').play()
		bullet_velocity = self.direction * self.BULLET_SPEED + self.velocity
		bullet = Bullet(self.position, bullet_velocity)
		c.BULLETS.append(bullet)
		c.STREAMS.append(pox_module.add_charge(ship_x + 300, ship_y + 300, int(random.randint(10, 30)), (255, 255, 0),
		                                       gravity=False))
		self.create_bullet_callback(bullet)


enterprise = Ship((1920, 1080), lambda bullet: c.BULLETS.append(bullet))

enterprise.rotate_image(c.SHIP, 0)
enterprise.draw(c.screen)


class Asteroid(GameObject):
	def __init__(self, position, create_asteroid_callback, size=4):
		self.create_asteroid_callback = create_asteroid_callback
		self.size = size
		self.hp = size * level.asteroid_hp
		self.hit = False
		self.rotation = 0
		size_to_scale = {5: 0.5, 4: 0.4, 3: 0.3, 2: 0.2, 1: 0.15}
		self.scale = size_to_scale[size]
		self.ASTEROID_IMAGE = random.choice(c.ROCK_IMAGES)
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


MAX_ASTEROIDS = 10
asteroids = []
ASTEROIDS = []
asteroid_count = 0
MIN_ASTEROID_DISTANCE = 200
MAX_ASTEROID_DISTANCE = 1000


def spawn_enemy(amount, new=True):
	MAX_ASTEROIDS = [amount in range(random.randint(1, 10))]

	while len(asteroids) < len(MAX_ASTEROIDS):
		for asteroid_count in range(ASTEROID_COUNT := len(MAX_ASTEROIDS)):
			while True:
				position = get_random_position(c.screen)

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
				for idx in range(0, len(asteroids)):
					if a == asteroids[idx]:
						continue
					if a.position.distance_to(asteroids[idx].position) < MIN_ASTEROID_DISTANCE:
						del asteroids[idx]
						break


def add_one_charge(x, y, amount, last):
	c.now = pg.time.get_ticks()
	if c.now > c.last + c.blastinterval:
		c.STREAMS.append(pox_module.add_charge(x, y, amount, (255, 255, 255), False))
		c.last = c.now
	return c.last


key = pg.key.get_pressed()
if key[K_KP_MINUS]:
	spawn_enemy(1, new=True)

# Spawn the asteroids
spawn_enemy(random.randint(1, MAX_ASTEROIDS), new=True)

c.STREAMS.append(add_one_charge(c.ship_x + 300, c.ship_y + 300, int(random.randint(10, 300)), c.last))


def asteroidium(level_instance):
	for _ in range(level_instance.asteroids):
		ASTEROIDS.append(Asteroid(get_random_position(
			pg.Surface((c.screen.get_width() * 4, c.screen.get_height() * 4))),
			asteroids.append, random.randint(1, 5)))


# asteroidium(level)


class Bullet(GameObject):
	def __init__(self, position, velocity):
		ang_delta = position.angle_to((mx, my))
		super().__init__(position, pg.transform.rotate(c.LASER_IMAGE, -ang_delta), -velocity)

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

	def update(self, screen):
		self.y += self.size / 1.3
		if self.y > c.screen.get_height():
			jig = STARS.index(self)
			STARS.pop(jig)

	def move(self, screen):
		self.x += self.size / 1.5

	def draw(self, screen):
		c.screen.blit(self.surface, (self.x, self.y))


def _get_particles():
	particles = [*STARS, *c.STREAMS, *pox_module.spriteGroup, *pfx_module.spriteGroup, *poof_module.spriteGroup]
	return particles


def _get_game_objects():
	game_objects = [*ASTEROIDS,
	                enterprise, *c.BULLETS]
	if enterprise and enterprise.visible:
		game_objects.append(enterprise)
	return game_objects


def length2(dx, dy):
	return dx * dx + dy * dy


STARS = []


def starfield(width, height, single=False):
	global STARS
	stars = []
	for i in range(100):
		stars.append(Star(random.randint(0, width), random.randint(0, height), random.randint(1, 2), (255, 255, 255)))
	if single:
		STARS = stars
	else:
		STARS = pg.sprite.Group(stars)


while c.running:
	c.screen.fill((0, 0, 10))
	starfield(random.randint(1, c.screen.get_width()), random.randint(1, c.screen.get_height()), single=True)
	c.screen.blit(c.BACKGROUND, (0, 0))

	if pg.event.get() == QUIT:
		c.running = False

	keys = pg.key.get_pressed()
	mx, my = pg.mouse.get_pos()
	mousebutton = pg.mouse.get_pressed()

	if mousebutton[0]:
		pg.mixer.Sound(f'{c.HOME_DIR}/assets/lasersound.wav').play()
		enterprise.shoot_guns(c.ship_x, c.ship_y)
		c.STREAMS.append(
			poof_module.add_smoke(enterprise.position.x + enterprise.x, enterprise.position.y + enterprise.y, 1000,
			                      (255, 180, 150)))

	if keys[K_ESCAPE]:
		c.running = False

	if keys[K_RETURN]:
		pg.mixer.Sound(f'{c.HOME_DIR}/assets/lasersound.wav').play()
		enterprise.shoot_guns(c.ship_x, c.ship_y)
		poof_module.add_smoke(enterprise.position.x + enterprise.x, enterprise.position.y + enterprise.y, 100)

		c.PARTICLES.append(
			ship_particle := pfx_module.add_stream(700, 700,
			                                       90, (255, 180, 0),
			                                       180, 10, 12, 0.6))

	c.NOW_MS = 0
	keys = pg.key.get_pressed()
	if c.NOW_MS > c.keypress + c.keyinterval:
		if keys[pygame.K_UP] or keys[pygame.K_w]:
			keypress = pygame.time.get_ticks()
			enterprise.strafe_y(5)
		if keys[pygame.K_DOWN] or keys[pygame.K_s]:
			keypress = pygame.time.get_ticks()
			enterprise.strafe_y(-5)
		if keys[pygame.K_LEFT] or keys[pygame.K_a]:
			draw_left()
			keypress = pygame.time.get_ticks()
			enterprise.strafe_x(-5)
		if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
			draw_right()
			keypress = pygame.time.get_ticks()
			enterprise.strafe_y(5)
		if keys[pygame.K_SPACE]:
			keypress = pygame.time.get_ticks()
			c.laserkey += 1
			if c.laserkey > c.laserinterval:
				pg.mixer.Sound(f'{c.HOME_DIR}/assets/lasersound.wav').play()
				enterprise.shoot_guns(c.ship_x, c.ship_y)
				c.STREAMS.append(
					poof_module.add_smoke(enterprise.position.x + enterprise.x, enterprise.position.y + enterprise.y,
					                      100))
				c.laserkey = 0

	c.frame += 1
	if c.frame > len(c.ANIMATIONS):
		c.frame = 0

	enterprise.update()
	enterprise.draw(c.screen)

	try:
		for i in c.STREAMS:
			if hasattr(i, 'update'):
				i.update(c.screen)
			if hasattr(i, 'draw'):
				i.draw(c.screen)
		c.STREAMS.clear()
		for s in STARS:
			s.update(c.screen)
			s.draw(c.screen)
			if s.y > c.screen.get_height():
				if s in STARS:
					STARS.remove(s)
	except RuntimeError as e:
		print(f"ERROR occurred in {e}")

	c.collidetime = pg.time.get_ticks()
	c.collision_delay = 150
	c.now = pygame.time.get_ticks()
	if c.now > c.collidetime + c.collision_delay:
		for rock in asteroids:
			if rock.collides_with_tolerance(asteroid, -15):
				random.choice([pg.mixer.Sound(f'{c.HOME_DIR}/assets/boom.wav').play(),
				               pg.mixer.Sound(f'{c.HOME_DIR}/assets/boom5.wav').play()])
				temp = asteroid.velocity
				asteroid.velocity = rock.velocity
				asteroid.rotdelta = -asteroid.rotdelta
				asteroid.position = wrap_position(asteroid.position + asteroid.velocity * 2, c.screen)
				rock.velocity = temp
				rock.position = wrap_position(rock.position + rock.velocity * 2, c.screen)
				c.collidetime = pg.time.get_ticks()
				break

	for bullet in c.BULLETS[:]:
		for asteroid in ASTEROIDS[:]:
			if asteroid.collides_with(bullet):
				random.choice([pg.mixer.Sound(f'{c.HOME_DIR}/assets/boom2.wav').play(),
				               pg.mixer.Sound(f'{c.HOME_DIR}/assets/boom5.wav').play()])
				asteroid.hp -= 1
				c.BULLETS.remove(bullet)
				asteroid.hit = 5
				if asteroid.hp < 1:
					c.SCORE += 1
					c.STREAMS.append(
						pox_module.add_charge(asteroid.position[0], asteroid.position[1], 300 * asteroid.size,
						                      (255, 0, 0),
						                      False))
					ASTEROIDS.remove(asteroid)
				break

	for bullet in c.BULLETS[:]:
		if not c.screen.get_rect().collidepoint(bullet.position):
			c.BULLETS.remove(bullet)

	if not enterprise and c.message == "YOU DIED":
		State = State.DIED_WATCHING_ROCKS
		c.once = True
		pg.event.clear()

	if not asteroids and enterprise and enterprise.visible:
		if c.once:
			c.lvl_timer = pg.time.get_ticks()
		c.once = False
		c.message = "ENEMIES FELLED"
		pg.mixer.Sound(f'{c.HOME_DIR}/assets/levelup.wav').play()
		c.msg_opacity = 255
		c.msg_rot = 1
		c.msg_sca = 1
		c.now = pg.time.get_ticks()
		State = State.NEXTLEVEL
		if c.now > c.lvl_timer + 2000:
			c.message = ""
			c.once = True
			enterprise.visible = False
			level.up()
			pg.event.clear()

	if len(c.ANIMATIONS) > 1:
		c.ANIMATIONS.pop()
		if len(c.ANIMATIONS) == 1:
			ANIMATIONS = [c.SHIP]

	for particle in _get_particles():
		particle.update(c.screen)
		if not hasattr(particle, 'rect'):
			particle.draw(random.randint(0, c.screen.get_width()))
			continue
		if not hasattr(particle, "blit"):
			print(particle, type(particle), dir(particle), particle.__dict__)
			# particle.move(c.screen)
			c.screen.blit(particle.surface, (0, c.screen.get_width()))
			continue
		else:
			c.screen.blit(particle, particle.rect)

	for game_object in _get_game_objects():

		if game_object is None:
			del game_object
			continue
		if is_int(str(game_object)):
			del game_object
			continue
		if hasattr(game_object, 'rotate_in_place'):
			game_object.rotate_in_place()
		if hasattr(game_object, 'move'):
			game_object.move(c.screen)
		if not hasattr(game_object, 'position') or not hasattr(game_object, 'draw'):
			c.screen.blit(game_object.image, game_object.rect)
		else:
			game_object.draw(c.screen)

	c.screen.blit(render_char("DarkVoid2 beta 0.0146", (100, 100, 255)), (10, 10))

	pg.display.flip()
	c.clock.tick(159)

	enterprise.update()
	enterprise.draw(c.screen)

	try:
		for i in c.STREAMS:
			if hasattr(i, 'update'):
				i.update(c.screen)
			if hasattr(i, 'draw'):
				i.draw(c.screen)
		c.STREAMS.clear()
		for s in STARS:
			s.update(c.screen)
			s.draw(c.screen)
			if s.y > c.screen.get_height():
				if s in STARS:
					STARS.remove(s)
	except RuntimeError as e:
		print(f"ERROR occurred in {e}")

	for b in pfx_module.stream:
		for p in pfx_module.spriteGroup:
			p.update(c.screen)
			c.screen.blit(p.image, (p.rect.x + enterprise.x, p.rect.y + enterprise.y + 500))
	pfx_module.stream.clear()

	ANIMATIONS = [c.SHIP]
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
		if game_object.collides_with_any(c.BULLETS):
			if isinstance(game_object, Asteroid):
				game_object.hp -= 1
				game_object.radius = game_object.sprite.get_width() / 2
				try:
					if game_object.hp <= 0:
						asteroids.remove(game_object)
					if game_object not in aASTEROIDS:
						continue
				except ValueError as e:
					print(f"{game_object}")
				c.STREAMS.append(
					add_one_charge(game_object.position.x, game_object.position.y, int(random.randint(10, 300)),
					               c.last))

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
			game_object.move(c.screen)

		if not hasattr(game_object, 'sprite'):
			continue
		c.screen.blit(game_object.sprite, game_object.position)

pg.quit()
pg.mixer.fadeout(2000)
pg.mixer.stop()
