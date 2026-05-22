import random
import pygame as pg
import config as c
from entities.explosion import Explosion
from entities.particle import Particle
from entities.powerup import PowerUp
from entities.level import Level

class Meteor(pg.sprite.Sprite):
	def __init__(self, game, pos):
		super().__init__()
		self.level = c.level.stage
		self.game = game
		self.pos = pg.Vector2(pos)
		self.pos.y = -100
		self.max_asteroids = c.level.max_asteroids
		self.image = random.choice(c.ROCK_IMAGES)
		scale = random.uniform(0.35, 1.05)

		w = int(self.image.get_width() * scale)
		h = int(self.image.get_height() * scale)
		self.image = pg.transform.scale(self.image, (w, h))

		self.base_image = self.image.copy()
		self.rect = self.image.get_rect(center=self.pos)

		self.velocity = pg.Vector2(
			random.uniform(-30, 30),
			random.uniform(80, 130)
		)

		self.rotation = random.uniform(0, 360)
		self.rotation_speed = random.uniform(-75, 75)

		self.hitbox = self.rect.inflate(-40, -40)
		self.hp = c.level.asteroid_hp

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
		if random.random() < 0.15:
			powerup = PowerUp(self.game, (random.randint(0, c.WIDTH), 0),
			                  random.choice(["health", "speed", "spread", "laser", "cannon"]))
			self.game.powerups.add(powerup)
			self.game.all_sprites.add(powerup)
		self.kill()
