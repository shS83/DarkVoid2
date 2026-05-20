import os
import pygame as pg
import config as c
from entities.bullet import PlayerBullet
from entities.explosion import Explosion
from entities.particle import Particle
from core.gameover_text import Gameover


class Player(pg.sprite.Sprite):
	def __init__(self, game, pos):
		super().__init__()
		self.lives = 3
		self.invincible_timer = 0
		self.alive = True
		self.hitbox_radius = 6
		self.fire_timer = 0
		self.fire_cooldown = 0.12
		self.game = game
		self.image = pg.image.load(f"{os.getcwd()}/assets/Proper_warship.png").convert_alpha()
		self.image = pg.transform.scale(self.image, (96, 96))
		self.rect = self.image.get_rect(center=pos)
		self.pos = pg.Vector2(self.rect.center)
		self.base_image = self.image.copy()
		self.flash_image = self.make_flash_image(self.base_image)
		self.flash_toggle_timer = 0
		self.speed = 350

	def make_flash_image(self, image):
		flash = pg.Surface(image.get_size(), pg.SRCALPHA)

		# Copy only the alpha channel shape from original image
		alpha_mask = image.copy()
		alpha_mask.fill((255, 255, 255, 255), special_flags=pg.BLEND_RGBA_MULT)

		flash.blit(alpha_mask, (0, 0))
		flash.fill((255, 255, 255, 255), special_flags=pg.BLEND_RGB_MAX)

		return flash

	def shoot(self):
		if self.fire_timer > 0:
			return
		pg.mixer.Sound(f'{os.getcwd()}/assets/lasersound2.wav').play()
		self.fire_timer = self.fire_cooldown
		bullet = PlayerBullet(self.game, self.rect.midtop)
		self.game.player_bullets.add(bullet)
		self.game.all_sprites.add(bullet)

	def hit(self):
		self.flash_timer = 0.05
		if self.invincible_timer > 0:
			return
		pg.mixer.Sound(f'{os.getcwd()}/assets/clink.wav').play()
		self.lives -= 1
		self.invincible_timer = 2.0
		for _ in range(100):
			particle = Particle(self.game, self.rect.center)
			self.game.effects.add(particle)
			self.game.all_sprites.add(particle)

		if self.lives <= 0:
			explosion_sound = f'{os.getcwd()}/assets/explosion1-long.wav'
			pg.mixer.Sound(explosion_sound).play()
			explosion = Explosion(self.game, self.rect.center)
			self.game.effects.add(explosion)
			self.game.all_sprites.add(explosion)
			for _ in range(10000):
				particle = Particle(self.game, self.rect.center)
				self.game.effects.add(particle)
				self.game.all_sprites.add(particle)
			self.alive = False
			self.game.gameover = True
			self.kill()

	def update(self, dt):
		keys = pg.key.get_pressed()
		mouse = pg.mouse.get_pressed()
		direction = pg.Vector2(0, 0)
		self.fire_timer -= dt
		if keys[pg.K_LEFT] or keys[pg.K_a]:
			direction.x -= 1
		if keys[pg.K_RIGHT] or keys[pg.K_d]:
			direction.x += 1
		if keys[pg.K_UP] or keys[pg.K_w]:
			direction.y -= 1
		if keys[pg.K_DOWN] or keys[pg.K_s]:
			direction.y += 1
		if keys[pg.K_SPACE] or mouse[0]:
			self.shoot()
		if keys[pg.K_ESCAPE]:
			pg.quit()
		if direction.length_squared() > 0:
			direction = direction.normalize()

		if self.invincible_timer > 0:
			self.flash_toggle_timer += dt
			self.invincible_timer -= dt

			if int(self.flash_toggle_timer * 12) % 2 == 0:
				self.image = self.flash_image
				self.image.set_alpha(255)
			else:
				self.image = self.base_image
				self.image.set_alpha(140)

		else:
			self.image = self.base_image
			self.image.set_alpha(255)

		self.pos += direction * self.speed * dt

		self.pos.x = max(32, min(c.WIDTH - 32, self.pos.x))
		self.pos.y = max(32, min(c.HEIGHT - 32, self.pos.y))

		self.rect.center = self.pos
