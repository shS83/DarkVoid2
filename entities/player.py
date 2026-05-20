import pygame as pg
import config as c
from entities.bullet import PlayerBullet
from entities.explosion import Explosion
from entities.particle import Particle
from entities.thruster_particle import ThrusterParticle
import random
from pygame.transform import rotozoom
from entities.powerup import PowerUp


class Player(pg.sprite.Sprite):
	def __init__(self, game, pos):
		super().__init__()
		self.shoot_mode = "normal"
		self.power_timer = 0
		self.lives = 3
		self.invincible_timer = 0
		self.thruster_timer = 0
		self.alive = True
		self.hitbox_radius = 6
		self.fire_timer = 0
		self.fire_cooldown = 0.10
		self.fire_cooldown2 = 0.08
		self.game = game
		self.image3 = rotozoom(pg.image.load(f"{c.HOME_DIR}/assets/purplealus.png").convert_alpha(), 0, 0.3)
		# self.image8 = rotozoom(pg.image.load(f"{c.HOME_DIR}/assets/turqoiseship.png").convert_alpha(), 0, 0.3)
		self.image1 = pg.image.load(f"{c.HOME_DIR}/assets/Proper_warship.png").convert_alpha()
		self.images = [self.image1, self.image3]
		self.image = random.choice(self.images)
		self.image = pg.transform.scale(self.image, (160, 160))
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

	def shoot_normal(self):
		bullet = PlayerBullet(self.game, self.rect.midtop, velocity=(0, -800))
		if self.fire_timer > 0:
			return
		pg.mixer.Sound(f'{c.HOME_DIR}/assets/lasersound2.wav').play()
		self.fire_timer = self.fire_cooldown2
		self.game.player_bullets.add(bullet)
		self.game.all_sprites.add(bullet)

	def shoot_spread(self):
		self.image = pg.Surface((6, 20), pg.SRCALPHA)
		pg.draw.rect(self.image, (255, 0, 0), (0, 0, 5, 25))
		bullet_data = [
			((self.rect.centerx, self.rect.top), (0, -850)),
			((self.rect.centerx - 10, self.rect.top + 8), (-180, -760)),
			((self.rect.centerx + 10, self.rect.top + 8), (180, -760)),
		]
		if self.fire_timer > 0:
			return
		pg.mixer.Sound(f'{c.HOME_DIR}/assets/lasersound.wav').play()
		self.fire_timer = self.fire_cooldown
		for pos, velocity in bullet_data:
			bullet = PlayerBullet(self.game, pos, velocity=velocity)
			self.game.player_bullets.add(bullet)
			self.game.all_sprites.add(bullet)

	def hit(self):
		self.flash_timer = 0.05
		if self.invincible_timer > 0:
			return
		pg.mixer.Sound(f'{c.HOME_DIR}/assets/clink.wav').play()
		self.lives -= 1
		self.invincible_timer = 2.0
		for _ in range(100):
			particle = Particle(self.game, self.rect.center)
			self.game.effects.add(particle)
			self.game.all_sprites.add(particle)

		if self.lives <= 0:
			explosion_sound = f'{c.HOME_DIR}/assets/explosion1-long.wav'
			pg.mixer.Sound(explosion_sound).play()
			explosion = Explosion(self.game, self.rect.center)
			self.game.effects.add(explosion)
			self.game.all_sprites.add(explosion)
			for _ in range(10000):
				particle = Particle(self.game, self.rect.center)
				self.game.effects.add(particle)
				self.game.all_sprites.add(particle)
			self.alive = False
			self.game.game_over = True
			self.kill()

	def apply_powerup(self, kind):
		self.timer = 300
		if kind == "spread":
			self.timer -= 1
			self.shoot_mode = "spread"
			self.power_timer = 12.0
		if kind == "speed":
			self.timer -= 1
			self.speed = 700
			self.power_timer = 12.0
		if kind == "laser":
			self.timer -= 1
			self.fire_cooldown2 = 0.01
			self.power_timer = 12.0
		if kind == "health":
			self.lives += 3

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
		if keys[pg.K_SPACE] or mouse[0] == 1:
			if self.shoot_mode == "spread":
				self.shoot_spread()
			else:
				self.shoot_normal()
		if keys[pg.K_LCTRL]:
			self.shoot_spread()

		if keys[pg.K_ESCAPE]:
			pg.quit()
		# For debugging
		if keys[pg.K_F9]:
			powerup = PowerUp(self.game, (self.rect.x, 0), kind=random.choice(["health", "speed", "spread", "laser"]))
			self.game.powerups.add(powerup)
			self.game.all_sprites.add(powerup)
		if keys[pg.K_F11]:
			self.alive = False
		if keys[pg.K_F10]:
			c.boss_time = True

		if self.power_timer > 0:
			self.power_timer -= dt

		if self.power_timer <= 0:
			self.shoot_mode = "normal"
			self.speed = 350

		self.thruster_timer -= dt

		if self.thruster_timer <= 0:
			self.thruster_timer = 0.012

			engine_left = (self.rect.centerx - 10, self.rect.centery + 42)
			engine_right = (self.rect.centerx + 10, self.rect.centery + 42)
			for engine_pos in [engine_left, engine_right]:
				# hot core
				for _ in range(1):
					particle = ThrusterParticle(
						self.game,
						engine_pos,
						direction=(0, 1),
						color=(255, 220, 235),
						speed_range=(280, 520),
						size_range=(1, 5),
						life_range=(0.12, 0.46),
						spread=18
					)
					self.game.effects.add(particle)
					self.game.all_sprites.add(particle)

				# purple/blue outer flame
				for _ in range(2):
					particle = ThrusterParticle(
						self.game,
						engine_pos,
						direction=(0, 1),
						color=(255, 115, 240),
						speed_range=(180, 380),
						size_range=(2, 6),
						life_range=(0.18, 0.38),
						spread=15
					)
					self.game.effects.add(particle)
					self.game.all_sprites.add(particle)

				# orange sparks
				if random.random() < 0.45:
					particle = ThrusterParticle(
						self.game,
						engine_pos,
						direction=(0, 1),
						color=(255, 140, 140),
						speed_range=(320, 700),
						size_range=(2, 4),
						life_range=(0.12, 0.22),
						spread=10
					)
					self.game.effects.add(particle)
					self.game.all_sprites.add(particle)

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
