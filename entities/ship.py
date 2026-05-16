from core.gameobject import GameObject
import pygame as pg
from pygame.math import Vector2
import pygame.transform as tf
import math
import core.commons as c
from entities.bullet import Bullet
from core.spritegroups import bullet_group
import random
from magic import pox_module


class Ship(GameObject):
	SHIP_SCALE = 0.6

	def __init__(self, position, image, bullet_group):
		super().__init__(position, image)
		self.visible = True
		self.bullet_group = bullet_group
		self.direction = Vector2(0, -1)
		self.speed = 0
		self.max_speed = 300

	def update(self, dt):
		keys = pg.key.get_pressed()

		if keys[pg.K_LEFT]:
			self.rotation += 180 * dt
		if keys[pg.K_RIGHT]:
			self.rotation -= 180 * dt

		# forward movement
		if keys[pg.K_UP]:
			self.velocity += self.direction * 200 * dt

		# clamp speed
		if self.velocity.length() > self.max_speed:
			self.velocity.scale_to_length(self.max_speed)

		self.direction = Vector2(
			math.cos(math.radians(self.rotation)),
			math.sin(math.radians(self.rotation))
		)

		self.image = tf.rotozoom(self.original_image, self.rotation, 0.6)
		self.rect = self.image.get_rect(center=self.position)

		super().update(dt)

	def shoot(self):
		bullet = Bullet(self.position, self.direction * 500)
		self.bullet_group.add(bullet)

	def draw(self, surface):
		angle = self.direction.angle_to(Vector2(0, 1))

		self.image = tf.rotozoom(
			self.original_image,
			angle,
			Ship.SHIP_SCALE
		)

		self.rect = self.image.get_rect(center=self.position)

		surface.blit(self.image, self.rect)

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
		pg.mixer.Sound(f'{c.HOME_DIR}/assets/lasersound.wav').play()
		bullet_velocity = self.direction * self.BULLET_SPEED + self.velocity
		bullet = Bullet(self.position, bullet_velocity)
		c.BULLETS.append(bullet)
		c.STREAMS.append(pox_module.add_charge(ship_x + 300, ship_y + 300, int(random.randint(10, 30)), (255, 255, 0),
		                                       gravity=False))
		self.create_bullet_callback(bullet)


enterprise = Ship((1920 // 2, 800), pg.image.load(f'{c.HOME_DIR}/assets/ship_neutral.png').convert_alpha(),
                  bullet_group)

enterprise.rotate_image(c.SHIP, 0)
enterprise.draw(c.screen)
