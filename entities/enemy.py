import pygame as pg
import config as c
from pygame.transform import rotozoom
import random
from pathlib import Path
from entities.explosion import Explosion
from entities.particle import Particle
from entities.bullet import EnemyBullet, RedPellet, BlueLaser
from entities.thruster_particle import ThrusterParticle
from entities.powerup import PowerUp


class Enemy(pg.sprite.Sprite):
	def __init__(self, game, pos, weapon_type:str = "normal" or "red_pellet" or "blue_laser", hp=5, shoot_delay=1.0, shoot_timer=1.4, name="Fred Grunt", image=pg.image.load(Path(c.HOME_DIR, "assets", "ships", "redhawk.png")), boss=False):
		super().__init__()
		self.image1 = rotozoom(
			pg.image.load(c.resource_path(Path(c.HOME_DIR, "assets", "ships", "purplealus.png"))).convert_alpha(), 180,
			c.SCALE)
		self.image2 = rotozoom(
			pg.image.load(c.resource_path(Path(c.HOME_DIR, "assets", "ships", "redhawk.png"))).convert_alpha(), 180,
			c.SCALE)
		self.image3 = rotozoom(
			pg.image.load(c.resource_path(Path(c.HOME_DIR, "assets", "ships", "turqoiseship.png"))).convert_alpha(),
			180, c.SCALE)
		self.image4 = rotozoom(
			pg.image.load(c.resource_path(Path(c.HOME_DIR, "assets", "ships", "redalus.png"))).convert_alpha(), 180,
			c.SCALE)
		self.image5 = rotozoom(
			pg.image.load(c.resource_path(Path(c.HOME_DIR, "assets", "ships", "grayship.png"))).convert_alpha(), 180,
			c.SCALE)
		self.image6 = rotozoom(
			pg.image.load(c.resource_path(Path(c.HOME_DIR, "assets", "ships", "bluehawk.png"))).convert_alpha(), 180,
			c.SCALE)
		self.image7 = rotozoom(
			pg.image.load(c.resource_path(Path(c.HOME_DIR, "assets", "ships", "blackhawk.png"))).convert_alpha(), 180,
			c.SCALE)
		self.image8 = rotozoom(
			pg.image.load(c.resource_path(Path(c.HOME_DIR, "assets", "ships", "orangeship.png"))).convert_alpha(), 180,
			c.SCALE)
		self.image9 = rotozoom(
			pg.image.load(c.resource_path(Path(c.HOME_DIR, "assets", "ships", "lilac-thrusters.png"))).convert_alpha(),
			180, c.SCALE)
		self.image10 = rotozoom(
			pg.image.load(c.resource_path(Path(c.HOME_DIR, "assets", "ships", "robotector.png"))).convert_alpha(), 180,
			c.SCALE)
		self.image11 = rotozoom(
			pg.image.load(c.resource_path(Path(c.HOME_DIR, "assets", "ships", "vihree-alus.png"))).convert_alpha(), 180,
			c.SCALE)
		self.images = [self.image1, self.image2, self.image3, self.image4, self.image5, self.image6, self.image7,
		               self.image8, self.image9, self.image10, self.image11]
		enemy_data = random.choice([
			{
				"name": "Boyscout",
				"image": self.image1,
				"weapon": "normal",
				"hp": 8,
				"shoot_timer": 0.8,
				"shoot_delay": 1.0
			},
			{
				"name": "Turbo",
				"image": self.image2,
				"weapon": "red_pellet",
				"hp": 8,
				"shoot_timer": 0.8,
				"shoot_delay": 1.0
			},
			{
				"name": "Redhawk",
				"image": self.image4,
				"weapon": "red_pellet",
				"hp": 8,
				"shoot_timer": 0.8,
				"shoot_delay": 1.0
			},
			{
				"name": "robotector",
				"image": self.image10,
				"weapon": "normal",
				"hp": 10,
				"shoot_timer": 0.6,
				"shoot_delay": 0.8
			},

			{
				"name": "Bluehawk",
				"image": self.image6,
				"weapon": "blue_laser",
				"hp": 7,
				"shoot_timer": 0.8,
				"shoot_delay": 2.0
			},
			{
				"name": "John Dark Void",
				"image": self.image3,
				"weapon": "blue_laser",
				"hp": 7,
				"shoot_timer": 0.8,
				"shoot_delay": 2.0
			},
			{
				"name": "the Lilac Thruster",
				"image": self.image9,
				"weapon": "blue_laser",
				"hp": 7,
				"shoot_timer": 0.8,
				"shoot_delay": 2.0
			},
			{
				"name": "Some Drone",
				"image": self.image5,
				"weapon": "normal",
				"hp": 5,
				"shoot_timer": 1.0,
				"shoot_delay": 1.4
			},
			{
				"name": "Blackhawk",
				"image": self.image7,
				"weapon": "normal",
				"hp": 5,
				"shoot_timer": 1.0,
				"shoot_delay": 1.4
			},
			{
				"name": "The Wasp",
				"image": self.image8,
				"weapon": "red_pellet",
				"hp": 7,
				"shoot_timer": 0.8,
				"shoot_delay": 1.2
			},
			{
				"name": "Swamp Thing",
				"image": self.image11,
				"weapon": "red_pellet",
				"hp": 9,
				"shoot_timer": 1.0,
				"shoot_delay": 1.4
			},

		])
		self.weapon_type = enemy_data.get("weapon", "normal")
		self.game = game
		self.image = enemy_data.get("image", pg.image.load(Path(c.HOME_DIR, "assets", "ships", "lilac-thrusters.png")).convert_alpha())
		self.name = enemy_data.get("name", "Jane Doe")
		self.thruster_timer = 0
		self.hp = enemy_data.get("hp", 5)
		self.shoot_timer = enemy_data.get("shoot_timer", 1.0)
		self.shoot_delay = enemy_data.get("shoot_delay", 1.4)
		self.mask = pg.mask.from_surface(self.image)

		if c.BOSS_TIME:
			self.boss_time = True
		else:
			self.boss_time = False
		if self.boss_time:
			self.boss = rotozoom(pg.image.load(c.resource_path(Path(c.HOME_DIR, "assets", "ships","bosses", "dark-crusader.png"))).convert_alpha(), 180, 1)
		self.boss_hp = 150

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
		self.rotation = 180

		if c.BOSS_TIME:
			self.hp = c.level.boss_hp
			self.speed = 40

	def make_flash_image(self, image):
		flash = pg.Surface(image.get_size(), pg.SRCALPHA)

		# Copy only the alpha channel shape from original image
		alpha_mask = image.copy()
		alpha_mask.fill((255, 255, 255, 200), special_flags=pg.BLEND_RGBA_MULT)

		flash.blit(alpha_mask, (0, 0))
		flash.fill((255, 255, 255, 200), special_flags=pg.BLEND_RGB_MAX)

		return flash

	def update(self, dt):
		self.pos.y += self.speed * dt
		direction = self.game.player.pos - self.pos

		if direction.length_squared() == 0:
			direction = pg.Vector2(0, 1)
		else:
			direction = direction.normalize()
		self.rotation = direction.angle_to(self.game.player.pos)
		self.mask = pg.mask.from_surface(self.image)

		self.rect = self.image.get_rect(center=self.pos)
		self.hitbox = self.rect.inflate(-40, -40)
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
			source_image = self.flash_image
		else:
			source_image = self.base_image

		self.image = pg.transform.rotozoom(
			source_image,
			self.rotation,
			1
		)
		self.rect.center = self.pos
		self.mask = pg.mask.from_surface(self.image)
		self.hitbox.center = self.rect.center
		if self.rect.top > c.HEIGHT:
			self.kill()

	def shoot(self):
		bullet = None
		direction = self.game.player.pos - self.pos

		if direction.length_squared() == 0:
			direction = pg.Vector2(0, 1)
		else:
			direction = direction.normalize()

		if self.weapon_type == "normal":
			bullet = EnemyBullet(self.game,  self.rect.center, direction * 240, owner = self.name)

		if self.weapon_type == "blue_laser":
			direction = self.game.player.pos - self.pos

			if direction.length_squared() == 0:
				direction = pg.Vector2(0, 1)
			else:
				direction = direction.normalize()

			bullet = BlueLaser(
				self.game,
				self.rect.center,
				direction * 520,
				owner = self.name
			)

		if self.weapon_type == "red_pellet":
			bullet = RedPellet(
				self.game,
				self.rect.center,
				direction * 240,
				owner = self.name
			)

		self.game.enemy_bullets.add(bullet)
		self.game.all_sprites.add(bullet)

	def damage(self, amount):
		self.hp -= amount
		self.flash_timer = 0.005
		pg.mixer.Sound(Path(c.HOME_DIR, "assets", "audio", "clink.wav")).play()
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
		explosion_sounds = [f'{c.HOME_DIR}/assets/audio/explosion2.wav', f'{c.HOME_DIR}/assets/audio/explosion1-long.wav',
		                    f'{c.HOME_DIR}/assets/audio/explosion3.wav']
		pg.mixer.Sound(random.choice(explosion_sounds)).play()

		explosion = Explosion(self.game, self.rect.center)
		self.game.effects.add(explosion)
		self.game.all_sprites.add(explosion)
		for _ in range(500):
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
