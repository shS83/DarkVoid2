import pygame as pg
import random
from entities.particle import Particle
from entities.thruster_particle import ThrusterParticle
from entities.explosion import Explosion
from entities.bullet import EnemyBullet, PlayerBullet
import config as c
from pygame.transform import rotozoom


class Boss(pg.sprite.Sprite):
	def __init__(self, game, pos, boss=True):
		super().__init__()
		self.game = game
		self.thruster_timer = 0
		self.shoot_timer = 0.05
		self.shoot_delay = 1.4
		self.pos = pg.Vector2(pos)
		self.hp = 300
		self.max_h = c.HEIGHT // 2
		self.phase_index = 0
		self.phase_timer = 1000
		self.image = rotozoom(pg.image.load(f"{c.HOME_DIR}/assets/alus2.png").convert_alpha(), 180, 1)
		self.base_image = self.image.copy()
		self.flash_image = self.make_flash_image(self.base_image)
		self.flash_timer = 0
		self.rect = self.image.get_rect(center=pos)
		self.hitbox = self.rect.inflate(-56, -56)
		self.pos = pg.Vector2(self.rect.center)
		self.shoot_timer = 1.0
		self.thruster_timer = 0.04
		self.speed = 40
		self.phases = [
			self.phase_intro,
			self.phase_radial,
			self.phase_spiral,
			self.phase_desperation,
		]

	def update(self, dt):
		self.phase_timer += dt
		self.phases[self.phase_index](dt)
		if not self.max_h:
			self.pos.y += self.speed * dt
			self.rect.center = self.pos
		self.hitbox.center = self.rect.center
		self.shoot_timer -= dt

		self.thruster_timer -= dt

		if self.thruster_timer <= 0:
			self.thruster_timer = 0.04

			particle = ThrusterParticle(
				self.game,
				self.rect.midtop,
				direction=(0, -1),
				color=(255, 120, 40)
			)

			self.game.effects.add(particle)
			self.game.all_sprites.add(particle)

		if self.shoot_timer <= 0:
			self.shoot_timer = self.shoot_delay
			self.shoot()

		if self.flash_timer > 0:
			self.flash_timer -= dt
			self.image = self.flash_image
		else:
			self.image = self.base_image

	def next_phase(self):
		self.phase_index += 1
		self.phase_timer = 0

	def phase_intro(self, dt):
		pass

	def phase_radial(self, dt):
		pass

	def phase_spiral(self, dt):
		pass

	def phase_desperation(self, dt):
		pass

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
		self.hitbox.center = self.rect.center
		self.shoot_timer -= dt

		self.thruster_timer -= dt

		if self.thruster_timer <= 0:
			self.thruster_timer = 0.04

			particle = ThrusterParticle(
				self.game,
				self.rect.midtop,
				direction=(0, -1),
				color=(255, 120, 40)
			)

			self.game.effects.add(particle)
			self.game.all_sprites.add(particle)

		if self.flash_timer > 0:
			self.flash_timer -= dt
			self.image = self.flash_image
		else:
			self.image = self.base_image
		if self.rect.top > c.HEIGHT:
			self.kill()

	def shoot(self):
		if self.shoot_timer <= 0:
			self.shoot_timer = self.shoot_delay

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

	def damage(self, amount):
		self.hp -= amount
		self.flash_timer = 0.005

		if self.hp <= 0:
			self.destroy()

	def destroy(self, dt=pg.time.Clock().tick(60) / 1000):
		explosion_sounds = [f'{c.HOME_DIR}/assets/explosion2.wav', f'{c.HOME_DIR}/assets/explosion1-long.wav',
		                    f'{c.HOME_DIR}/assets/explosion3.wav']
		pg.mixer.Sound(random.choice(explosion_sounds)).play()
		now = pg.time.get_ticks()
		if dt + now > 1000:
			pg.mixer.Sound(random.choice(explosion_sounds)).play()
		if dt + now > 1500:
			pg.mixer.Sound(random.choice(explosion_sounds)).play()

		explosion = Explosion(self.game, self.rect.center)
		self.game.effects.add(explosion)
		self.game.all_sprites.add(explosion)
		now = pg.time.get_ticks()
		if dt + now > 100:
			explosion = Explosion(self.game, self.rect.center)
			self.game.effects.add(explosion)
			self.game.all_sprites.add(explosion)
		if dt + now > 300:
			explosion = Explosion(self.game, self.rect.center)
			self.game.effects.add(explosion)
			self.game.all_sprites.add(explosion)

		for _ in range(10000):
			particle = Particle(self.game, self.rect.center)
			self.game.effects.add(particle)
			self.game.all_sprites.add(particle)
		self.game.score += 5000
		self.kill()
