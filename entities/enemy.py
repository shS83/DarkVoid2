import pygame as pg
import config as c
from pygame.transform import rotozoom
import random
from pathlib import Path
from entities.explosion import Explosion
from entities.particle import Particle
from entities.bullet import EnemyBullet
from entities.thruster_particle import ThrusterParticle
from entities.powerup import PowerUp


class Enemy(pg.sprite.Sprite):
	def __init__(self, game, pos, boss=False):
		super().__init__()
		self.game = game
		self.thruster_timer = 0
		self.shoot_timer = 1.0
		self.shoot_delay = 1.4
		if c.BOSS_TIME:
			self.boss_time = True
		else:
			self.boss_time = False
		if self.boss_time:
			self.boss = rotozoom(pg.image.load(Path(c.HOME_DIR, "assets", "dark-crusader.png")).convert_alpha(), 180, 1)
		self.boss_hp = 150
		self.image1 = rotozoom(pg.image.load(Path(c.HOME_DIR, "assets", "purplealus.png")).convert_alpha(), 180, c.SCALE)
		self.image2 = rotozoom(pg.image.load(Path(c.HOME_DIR, "assets", "redhawk.png")).convert_alpha(), 180, c.SCALE)
		self.image3 = rotozoom(pg.image.load(Path(c.HOME_DIR, "assets", "turqoiseship.png")).convert_alpha(), 180, c.SCALE)
		self.image4 = rotozoom(pg.image.load(Path(c.HOME_DIR, "assets", "redalus.png")).convert_alpha(), 180, c.SCALE)
		self.image5 = rotozoom(pg.image.load(Path(c.HOME_DIR, "assets", "grayship.png")).convert_alpha(), 180, c.SCALE)
		self.image6 = rotozoom(pg.image.load(Path(c.HOME_DIR, "assets", "bluehawk.png")).convert_alpha(), 180, c.SCALE)
		self.image7 = rotozoom(pg.image.load(Path(c.HOME_DIR, "assets", "blackhawk.png")).convert_alpha(), 180, c.SCALE)
		self.image8 = rotozoom(pg.image.load(Path(c.HOME_DIR, "assets", "greenhawk.png")).convert_alpha(), 180, c.SCALE)
		self.image9 = rotozoom(pg.image.load(Path(c.HOME_DIR, "assets", "yellowhawk.png")).convert_alpha(), 180, c.SCALE)
		self.image10 = rotozoom(pg.image.load(Path(c.HOME_DIR, "assets", "orangehawk.png")).convert_alpha(), 180, c.SCALE)
		self.image11 = rotozoom(pg.image.load(Path(c.HOME_DIR, "assets", "pinkhawk.png")).convert_alpha(), 180, c.SCALE)
		self.image12 = rotozoom(pg.image.load(Path(c.HOME_DIR, "assets", "purplehawk.png")).convert_alpha(), 180, c.SCALE)
		self.image13 = rotozoom(pg.image.load(Path(c.HOME_DIR, "assets", "robotector.png")).convert_alpha(), 180, c.SCALE)
		self.image14 = rotozoom(pg.image.load(Path(c.HOME_DIR, "assets", "lilac-thrusters.png")).convert_alpha(), 180, c.SCALE)
		self.images = [self.image1, self.image2, self.image3, self.image4, self.image5, self.image6, self.image7, self.image8, self.image9, self.image10, self.image11, self.image12, self.image13, self.image14]
		if self.boss_time:
			self.image = self.boss
			self.base_image = self.boss.copy()
		else:
			self.image = random.choice(self.images)
			self.base_image = self.image.copy()
		self.flash_image = self.make_flash_image(self.base_image)
		self.flash_timer = 0.05
		self.rect = self.image.get_rect(center=pos)
		self.hitbox = self.rect.inflate(-56, -56)
		self.pos = pg.Vector2(self.rect.center)
		self.speed = 80
		self.hp = 5

		if c.BOSS_TIME:
			self.hp = c.level.boss_hp
			self.speed = 40

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
			direction * c.ENEMY_BULLET_SPEED
		)

		self.game.enemy_bullets.add(bullet)
		self.game.all_sprites.add(bullet)

	def damage(self, amount):
		self.hp -= amount
		self.flash_timer = 0.005
		pg.mixer.Sound(f'{c.HOME_DIR}/assets/clink.wav').play()
		COLORS = [(255, 0, 0), (255, 120, 40), (255, 255, 0), (255, 0, 255),
		          (0, 255, 255), (255, 255, 255)]
		colors = random.choice(COLORS)
		for _ in range(50):
			particle = Particle(self.game, self.rect.center, colors)
			self.game.effects.add(particle)
			self.game.all_sprites.add(particle)

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
		self.game.score += 100
		if random.random() < 0.15:
			(self.px,
			 self.py) = random.randrange(0, c.WIDTH), random.randrange(-150, -50)
			powerup = PowerUp(self.game, (random.randint(0, c.WIDTH), 0),
			                  random.choice(["health", "speed", "spread", "laser", "cannon", "shield"]))
			self.game.powerups.add(powerup)
			self.game.all_sprites.add(powerup)
		self.kill()
