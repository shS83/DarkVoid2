import random
import pygame as pg
import config as c
from core import commons
from entities.explosion import Explosion
from entities.particle import Particle
from entities.powerup import PowerUp
from core.utils import get_random_position


class Meteor(pg.sprite.Sprite):
	def __init__(self, game, pos):
		super().__init__()

		self.game = game
		self.pos = pg.Vector2(pos)

		self.image = random.choice(commons.ROCK_IMAGES).copy()
		scale = random.uniform(0.35, 1.05)

		w = int(self.image.get_width() * scale)
		h = int(self.image.get_height() * scale)
		self.image = pg.transform.scale(self.image, (w, h))

		self.base_image = self.image.copy()
		self.rect = self.image.get_rect(center=self.pos)

		self.velocity = pg.Vector2(
			random.uniform(-60, 60),
			random.uniform(90, 210)
		)

		self.rotation = random.uniform(0, 360)
		self.rotation_speed = random.uniform(-100, 100)

		self.hitbox = self.rect.inflate(-40, -40)
		self.hp = 3

	def update(self, dt):
		self.pos += self.velocity * dt

		self.rotation += self.rotation_speed * dt
		center = self.pos

		self.image = pg.transform.rotozoom(
			self.base_image,
			self.rotation,
			1
		)

		self.rect = self.image.get_rect(center=center)
		self.hitbox = self.rect.inflate(-40, -40)

		if self.rect.top > c.HEIGHT + 80:
			self.kill()

	def damage(self, amount):
		self.hp -= amount

		if self.hp <= 0:
			self.destroy()

	def destroy(self):
		explosion_sounds = [f'{c.HOME_DIR}/assets/explosion2.wav', f'{c.HOME_DIR}/assets/explosion1-long.wav',
		                    f'{c.HOME_DIR}/assets/explosion3.wav']
		pg.mixer.Sound(random.choice(explosion_sounds)).play()

		explosion = Explosion(self.game, self.rect.center)
		self.game.effects.add(explosion)
		self.game.all_sprites.add(explosion)
		for _ in range(5000):
			particle = Particle(self.game, self.rect.center)
			self.game.effects.add(particle)
			self.game.all_sprites.add(particle)
		self.game.score += 50
		if random.random() < 0.3:
			self.px, self.py = get_random_position(c.screen)
			powerup = PowerUp(self.game, (random.randint(0, c.WIDTH), 0),
			                  random.choice(["health", "speed", "spread", "laser"]))
			self.game.powerups.add(powerup)
			self.game.all_sprites.add(powerup)
		self.kill()
