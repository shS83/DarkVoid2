import pygame as pg
from entities.events import Event
from entities.particle import Particle
from entities.thruster_particle import ThrusterParticle
from entities.explosion import Explosion
from entities.bullet import EnemyBullet
import config as c
from pygame.transform import rotozoom
from entities.level import *
from pathlib import Path

class Boss(pg.sprite.Sprite):
	def __init__(self, game, pos, boss=True):
		super().__init__()
		self.game = game
		self.thruster_timer = 0
		self.shoot_timer = 0.001
		self.shoot_delay = 0.001
		self.pos = pg.Vector2(pos)
		self.pos.y = -c.level.boss_timer
		self.entering = True
		self.hp = 300
		self.phase_index = 0
		self.phase_timer = 0
		self.boss_timer = c.level.boss_timer
		self.image = rotozoom(pg.image.load(Path(c.HOME_DIR, "assets", "alus2.png")).convert_alpha(), 180, 1)
		self.max_h = 160
		self.hitbox = self.rect = self.image.get_rect(center=pos).inflate(-300, -300)
		self.base_image = self.image.copy()
		self.flash_image = self.make_flash_image(self.base_image)
		self.flash_timer = 0
		self.rect = self.image.get_rect(center=pos)
		self.pos = pg.Vector2(self.rect.center)
		self.thruster_timer = 0.04
		self.speed = 30
		self.phases = [
			self.phase_intro,
			self.phase_radial,
			self.phase_spiral,
			self.phase_desperation,
		]

	def update(self, dt):
		if self.pos.y < self.max_h:
			self.entering = True
			self.pos.y += self.speed * dt
		else:
			self.entering = False
			self.pos.y = self.max_h

		if self.pos.y < self.max_h:
			self.pos.y += self.speed * dt
			if self.pos.y > self.max_h:
				self.pos.y = self.max_h

		self.rect.center = self.pos
		self.hitbox.center = self.rect.center

		self.shoot_timer -= dt
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

		if self.flash_timer > 0:
			self.flash_timer -= dt
			self.image = self.flash_image
		else:
			self.image = self.base_image

	def next_phase(self):
		self.phase_index += 1
		self.phase_timer = 1

	def fire_bullet(self, pos, velocity):
		self.shoot_timer = 0
		self.shoot_delay = 1.5
		print("fire bullet phase")
		if self.shoot_timer <= self.shoot_delay:
			self.shoot_timer = self.shoot_delay
			bullet = EnemyBullet(self.game, pos, velocity)
		self.game.enemy_bullets.add(bullet)
		self.game.all_sprites.add(bullet)

	def aimed_shot(self, speed=260):
		self.shoot_timer = 0
		self.shoot_delay = 1.5
		direction = self.game.player.pos - self.pos
		print("aimed shot phase")
		if direction.length_squared() == 0:
			direction = pg.Vector2(0, 1)
		else:
			direction = direction.normalize()
		if self.shoot_timer <= self.shoot_delay:
			self.shoot_timer = self.shoot_delay
			self.fire_bullet(self.rect.center, direction * speed * 50)

	def aimed_spread(self, count=7, speed=260, spread=50):
		self.shoot_timer = 0
		self.shoot_delay = 1.5
		direction = self.game.player.pos - self.pos
		print("aimed spread phase")
		if direction.length_squared() == 0:
			direction = pg.Vector2(0, 1)
		else:
			direction = direction.normalize()

		start = -spread / 2
		step = spread / max(1, count - 1)

		if self.shoot_timer <= self.shoot_delay:
			self.shoot_timer = self.shoot_delay
			for i in range(count):
				angle = start + step * i
				self.fire_bullet(
					self.rect.center,
					direction.rotate(angle) * speed
				)

	def radial_burst(self, count=32, speed=190, offset=0):
		self.shoot_timer = 0
		self.shoot_delay = 1.5
		print("radial burst")
		for i in range(count):
			angle = offset + 360 * i / count
			direction = pg.Vector2(1, 0).rotate(angle)

			if self.shoot_timer <= self.shoot_delay:
				self.shoot_timer = self.shoot_delay
				self.fire_bullet(
					self.rect.center,
					direction * speed
				)

	def spiral_burst(self, arms=4, speed=220):
		self.shoot_timer = 0
		self.shoot_delay = 1.5
		print("spiral burst")
		base_angle = self.phase_timer * 180

		for i in range(arms):
			angle = base_angle + i * (360 / arms)
			direction = pg.Vector2(1, 0).rotate(angle)
		if self.shoot_timer <= self.shoot_delay:
			self.shoot_timer = self.shoot_delay
			self.fire_bullet(
				self.rect.center,
				direction * speed
			)

	def phase_intro(self, dt):
		self.shoot_delay = 1.5
		print("intro phase")
		if self.phase_timer > 3:
			self.next_phase()

	def phase_radial(self, dt):
		self.shoot_delay = 1.5
		print("radial phase")
		if self.shoot_timer <= 0:
			self.shoot_timer = self.shoot_delay
			self.radial_burst(count=28, speed=180, offset=self.phase_timer)

		if self.phase_timer > 10:
			self.next_phase()

	def phase_spiral(self, dt):
		self.shoot_delay = 1.5
		print("spiral phase")
		if self.shoot_timer <= 0:
			self.shoot_timer = self.shoot_delay
			self.spiral_burst(arms=5, speed=230)

		if self.phase_timer > 10:
			self.next_phase()

	def phase_desperation(self, dt):
		self.shoot_delay = 1.5
		print("desperate phase")
		if self.shoot_timer <= 0:
			self.shoot_timer = self.shoot_delay
			self.aimed_spread(count=9, speed=300, spread=70)
			self.radial_burst(count=18, speed=210, offset=self.phase_timer * 90)

	def make_flash_image(self, image):
		flash = pg.Surface(image.get_size(), pg.SRCALPHA)

		# Copy only the alpha channel shape from original image
		alpha_mask = image.copy()
		alpha_mask.fill((255, 255, 255, 200), special_flags=pg.BLEND_RGBA_MULT)

		flash.blit(alpha_mask, (0, 0))
		flash.fill((255, 255, 255, 200), special_flags=pg.BLEND_RGB_MAX)

		return flash

	def shoot(self):
		self.shoot_delay = 1.5
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
		if self.entering:
			return

		self.hp -= amount
		self.flash_timer = 0.02

		if self.hp <= 0:
			self.destroy()

	def destroy(self, dt=pg.time.Clock().tick(60) / 1000):
		explosion = None
		interval = 400
		explosion_sounds = [f'{c.HOME_DIR}/assets/explosion2.wav', f'{c.HOME_DIR}/assets/explosion1-long.wav',
		                    f'{c.HOME_DIR}/assets/explosion3.wav']
		pg.mixer.Sound(random.choice(explosion_sounds)).play()
		now = pg.time.get_ticks()
		if dt + now > 1000 + interval:
			pg.mixer.Sound(random.choice(explosion_sounds)).play()

		if not explosion:
			explosion = Explosion(self.game, self.rect.center, boss=True)
			self.game.effects.add(explosion)
			self.game.all_sprites.add(explosion)

		for _ in range(5000):
			particle = Particle(self.game, self.rect.center)
			self.game.effects.add(particle)
			self.game.all_sprites.add(particle)

		self.game.score += 5000
		self.kill()
		self.game.boss_killed = True
		self.game.boss = Boss(self.game, (0, 0), boss=False)
		self.game.boss.image = pg.image.load(Path(c.HOME_DIR , "assets", "foobarhead1.png")).convert_alpha()
		self.game.boss.rect = self.game.boss.image.get_rect(center=self.game.boss.rect.center)
		self.game.boss.hitbox = self.rect.inflate(-100, -100)
		self.game.player.hp = 5
		# Man you got to level 2
		c.event = Event.NEXTLEVEL
		c.level.stage += 1
