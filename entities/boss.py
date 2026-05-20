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
		self.shoot_delay = 0.2
		self.pos = pg.Vector2(pos)
		self.hp = 500
		self.max_h = c.HEIGHT // 2
		self.phase_index = 0
		self.phase_timer = 1000
		self.image = rotozoom(pg.image.load(f"{c.HOME_DIR}/assets/alus2.png").convert_alpha(), 180, 1)
		self.hitbox = self.rect = self.image.get_rect(center=pos).inflate(-300, -300)
		game.screen.blit(self.rect, (255, 0, 0))
		self.base_image = self.image.copy()
		self.flash_image = self.make_flash_image(self.base_image)
		self.flash_timer = 0
		self.rect = self.image.get_rect(center=pos)
		self.pos = pg.Vector2(self.rect.center)
		self.shoot_timer = 0.05
		self.thruster_timer = 0.04
		self.speed = 30
		self.phases = [
			self.phase_intro,
			self.phase_radial,
			self.phase_spiral,
			self.phase_desperation,
		]

	def update(self, dt):
		if self.pos.y <= self.max_h:
			self.pos.y += self.speed * dt
		self.rect.center = self.pos
		self.hitbox.center = self.rect.center
		self.shoot_timer -= dt
		if self.shoot_timer < 1:
			self.shoot()

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
		self.phase_timer += dt
		self.phases[self.phase_index](dt)

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
		alpha_mask.fill((255, 255, 255, 200), special_flags=pg.BLEND_RGBA_MULT)

		flash.blit(alpha_mask, (0, 0))
		flash.fill((255, 255, 255, 200), special_flags=pg.BLEND_RGB_MAX)

		return flash

	def shoot(self):
		self.shoot_timer = self.shoot_delay

		direction = self.game.player.pos - self.pos

		if direction.length_squared() == 0:
			direction = self.game.player.pos - self.pos
		else:
			direction = direction.normalize()

		bullet = EnemyBullet(
			self.game,
			self.rect.center,
			direction
		)

		self.game.enemy_bullets.add(bullet)
		self.game.all_sprites.add(bullet)

	def damage(self, amount):
		self.hp -= amount
		self.flash_timer = 0.002

		if self.hp <= 0:
			self.destroy()

	def destroy(self, dt=pg.time.Clock().tick(60) / 1000):
		explosion_sounds = [f'{c.HOME_DIR}/assets/explosion2.wav', f'{c.HOME_DIR}/assets/explosion1-long.wav',
		                    f'{c.HOME_DIR}/assets/explosion3.wav']
		pg.mixer.Sound(random.choice(explosion_sounds)).play()
		now = pg.time.get_ticks()
		if dt + now > 1000:
			pg.mixer.Sound(random.choice(explosion_sounds)).play()
		if dt + now > 15400:
			pg.mixer.Sound(random.choice(explosion_sounds)).play()

		explosion = Explosion(self.game, self.rect.center)
		self.game.effects.add(explosion)
		self.game.all_sprites.add(explosion)
		now = pg.time.get_ticks()
		if dt + now > 1400:
			explosion = Explosion(self.game, self.rect.center)
			self.game.effects.add(explosion)
			self.game.all_sprites.add(explosion)
		if dt + now > 3500:
			explosion = Explosion(self.game, self.rect.center)
			self.game.effects.add(explosion)
			self.game.all_sprites.add(explosion)

		for _ in range(20000):
			particle = Particle(self.game, self.rect.center)
			self.game.effects.add(particle)
			self.game.all_sprites.add(particle)
		if dt + now > 4000:
			for _ in range(10000):
				particle = Particle(self.game, self.rect.center)
				self.game.effects.add(particle)
				self.game.all_sprites.add(particle)
		self.game.score += 5000
		self.kill()
