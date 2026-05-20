import pygame as pg
import config as c
from pygame.transform import rotozoom
import os
import random
from entities.explosion import Explosion
from entities.particle import Particle
from entities.bullet import EnemyBullet


class Enemy(pg.sprite.Sprite):
	def __init__(self, game, pos):
		super().__init__()

		self.game = game
		self.shoot_timer = 1.0
		self.shoot_delay = 1.4
		self.image = rotozoom(pg.image.load("assets/alus2.png").convert_alpha(), 180, 0.3)
		self.base_image = self.image.copy()
		self.flash_image = self.make_flash_image(self.base_image)
		self.flash_timer = 0
		self.rect = self.image.get_rect(center=pos)
		self.pos = pg.Vector2(self.rect.center)

		self.hp = 5
		self.speed = 80

	def make_flash_image(self, image):
		flash = pg.Surface(image.get_size(), pg.SRCALPHA)

		# Copy only the alpha channel shape from original image
		alpha_mask = image.copy()
		alpha_mask.fill((255, 255, 255, 255), special_flags=pg.BLEND_RGBA_MULT)

		flash.blit(alpha_mask, (0, 0))
		flash.fill((255, 255, 255, 255), special_flags=pg.BLEND_RGB_MAX)

		return flash

	def update(self, dt):
		self.pos.y += self.speed * dt
		self.rect.center = self.pos
		self.shoot_timer -= dt
		if self.shoot_timer <= 0:
			self.shoot_timer = self.shoot_delay
			self.shoot()

		if self.flash_timer > 0:
			self.flash_timer -= dt
			self.image = self.flash_image
		else:
			self.image = self.base_image
		if self.rect.top > c.HEIGHT:
			self.kill()

	def shoot(self):
		direction = self.game.player.pos - self.pos

		if direction.length_squared() == 0:
			direction = pg.Vector2(0, 1)
		else:
			direction = direction.normalize()

		bullet = EnemyBullet(
			self.game,
			self.rect.center,
			direction * 260
		)

		self.game.enemy_bullets.add(bullet)
		self.game.all_sprites.add(bullet)

	def damage(self, amount):
		self.hp -= amount
		self.flash_timer = 0.005

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

		self.kill()
