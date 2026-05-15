from core.gameobject import GameObject
from pygame.math import Vector2
import random
import pygame.transform as tf
from core.utils import get_random_position
from core import commons as c
from core.spritegroups import asteroid_group
import pygame as pg


class Asteroid(GameObject):
	MAX_ASTEROIDS = 10
	ASTEROID_COUNT = 0
	MIN_ASTEROID_DISTANCE = 200
	MAX_ASTEROID_DISTANCE = 1000

	def __init__(self, position, image, size, create_callback):
		self.size = size
		self.create_callback = create_callback

		self.scale = {5: 0.5, 4: 0.4, 3: 0.3, 2: 0.2, 1: 0.15}[size]

		super().__init__(
			position,
			image,
			velocity=Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
		)

		self.rotation_speed = random.uniform(-2, 2)

		self.image = tf.rotozoom(self.original_image, 0, self.scale)
		self.rect = self.image.get_rect(center=position)

	def update(self, dt):
		self.rotation += self.rotation_speed * dt

		self.image = tf.rotozoom(
			self.original_image,
			self.rotation,
			self.scale
		)

		super().update(dt)


def spawn_rock(amount, new=True):
	MAX_ASTEROIDS = [amount in range(random.randint(1, 10))]

	while len(asteroid_group) < len(MAX_ASTEROIDS):
		for ASTEROID_COUNT in range(ASTEROID_COUNT := len(MAX_ASTEROIDS)):
			while True:
				position = get_random_position(c.screen)

				if new:
					print(f"new on {position}")
					position = Vector2(-100, -100)
					new = False

				if (
						position.distance_to(enterprise.position)
						> Asteroid.MIN_ASTEROID_DISTANCE
				):
					break

			for r in c.ROCK_IMAGES:
				screen_rect = pg.Rect(0, 0, c.screen.get_width(), c.screen.get_height())
				asteroid_group.add(Asteroid(get_random_position(screen_rect), r, random.randint(1, 5), None))


def asteroidium(level_instance):
	for _ in range(level_instance.asteroids):
		screen_rect = pg.Rect(0, 0, c.screen.get_width(), c.screen.get_height())
		asteroid_group.add(Asteroid(get_random_position(screen_rect), pg.image.load(random.choice(c.ROCK_IMAGES)),
		                            random.randint(1, 5), None))
