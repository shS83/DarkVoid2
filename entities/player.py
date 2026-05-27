import math
import pygame as pg
from pathlib import Path
import config as c
from entities.vulcan import VulcanBullet, MuzzleFlash, VulcanSpark, ShellCasing
from pygame import mouse
from entities.bullet import PlayerBullet
from entities.explosion import Explosion
from entities.particle import Particle
from entities.thruster_particle import ThrusterParticle
from pygame.transform import rotate, smoothscale_by
import random
from entities.powerup import PowerUp

class Player(pg.sprite.Sprite):
	def __init__(self, game, pos):
		super().__init__()
		self.bullet = PlayerBullet(game, pos, velocity=(0, -800))
		self.game = game
		self.shoot_mode = "normal"
		self.power_timer = 0
		self.lives = self.game.level.lives
		self.invincible_timer = 0
		self.thruster_timer = 0
		self.alive = True
		self.fire_timer = 0
		self.fire_cooldown = 0.01
		self.fire_cooldown2 = 0.08
		self.fire_cooldown3 = 0.35
		self.game = game
		self.pauseswitch = -1
		self.image1 = smoothscale_by(pg.image.load(Path(c.HOME_DIR, "assets", "ships", "Proper_warship.png")).convert_alpha(), c.SCALE)
		self.image2 = smoothscale_by(rotate(pg.image.load(Path(c.HOME_DIR, "assets", "ships", "lilac-thrusters.png")).convert_alpha(), 180), c.SCALE)
		self.image3 = smoothscale_by(pg.image.load(Path(c.HOME_DIR, "assets", "ships", "purplealus.png")).convert_alpha(), c.SCALE)
		self.image4 = smoothscale_by(pg.image.load(Path(c.HOME_DIR, "assets", "ships", "turqoiseship.png")).convert_alpha(), c.SCALE)
		self.image5 = smoothscale_by(pg.image.load(Path(c.HOME_DIR, "assets", "ships", "finnfighter.png")).convert_alpha(), c.SCALE)
		self.images = [self.image5]#self.image1, self.image2, self.image3, self.image4]
		self.image = random.choice(self.images)
		self.image = pg.transform.smoothscale(self.image, (200, 200))
		self.rect = self.image.get_rect(center=pos)
		self.pos = pg.Vector2(self.rect.center)
		self.base_image = self.image.copy()
		self.flash_image = self.make_flash_image(self.base_image)
		self.flash_toggle_timer = 0
		self.speed = c.PLAYER_SPEED
		self.focus_speed = c.PLAYER_FOCUS_SPEED
		self.fire_cooldown = c.PLAYER_FIRE_COOLDOWN
		self.bullet_speed = c.PLAYER_BULLET_SPEED
		self.hitbox_radius = c.PLAYER_HITBOX_RADIUS
		self.particles = pg.sprite.Group()
		self.all_sprites = pg.sprite.LayeredUpdates()
		self.shield = False
		self.shield_image = pg.transform.scale(random.choice(c.PALLOT), (160, 160))
		self.shield_image_rect = self.shield_image.get_rect(center=pos)
		self.shield_active = False
		self.shield_amount = 0
		self.vulcan_timer = 0
		self.vulcan_cooldown = 0.028

		self.vulcan_side = -1
		self.vulcan_counter = 0

		self.vulcan_sound_timer = 0
		self.vulcan_sound_delay = 0.07

		self.minigun_sound = pg.mixer.Sound(f"{c.HOME_DIR}/assets/audio/gundam-vulcan-machine-gun-sound.mp3")
		self.minigun_sound.set_volume(0.4)

	def make_flash_image(self, image):
		flash = pg.Surface(image.get_size(), pg.SRCALPHA)

		# Copy only the alpha channel shape from original image
		alpha_mask = image.copy()
		alpha_mask.fill((255, 255, 255, 255), special_flags=pg.BLEND_RGBA_MULT)

		flash.blit(alpha_mask, (0, 0))
		flash.fill((255, 255, 255, 255), special_flags=pg.BLEND_RGB_MAX)

		return flash

	def shoot_vulcan(self, dt):
		self.vulcan_timer -= dt

		if self.vulcan_timer > 0:
			return

		self.vulcan_timer = self.vulcan_cooldown
		self.vulcan_counter += 1

		mx, my = pg.mouse.get_pos()

		# alternate left / right muzzle
		if self.vulcan_side == 0:
			muzzle = pg.Vector2(self.rect.centerx - 12, self.rect.centery - 26)
			self.vulcan_side = 1
		else:
			muzzle = pg.Vector2(self.rect.centerx + 12, self.rect.centery - 26)
			self.vulcan_side = 0

		target = pg.Vector2(mx, my)
		direction = target - muzzle

		if direction.length_squared() == 0:
			direction = pg.Vector2(0, -1)
		else:
			direction = direction.normalize()

		# slight inaccuracy = more realistic vulcan spread
		spread_angle = random.uniform(-4, 4)
		direction = direction.rotate(spread_angle)

		bullet_speed = 1400
		velocity = direction * bullet_speed
		angle = math.atan2(direction.y, direction.x)

		tracer = (self.vulcan_counter % 5 == 0)

		bullet = PlayerBullet(
			self.game,
			muzzle,
			angle,
			velocity=velocity,
			tracer=tracer
		)

		self.game.player_bullets.add(bullet)
		self.game.all_sprites.add(bullet)

		# small muzzle flash particles, not 500
		for _ in range(4):
			particle = Particle(self.game, muzzle)
			particle.velocity = pg.Vector2(
				random.uniform(-60, 60),
				random.uniform(-120, 30)
			)
			particle.life = random.uniform(0.04, 0.12)
			particle.max_life = particle.life
			self.game.effects.add(particle)
			self.game.all_sprites.add(particle)

		self.game.play_sound(self.minigun_sound, 0.2)

	def shoot_railgun(self):
		self.image = pg.transform.scale(pg.image.load(Path(c.HOME_DIR, "assets", "laser_2.png")), (20, 100))
		self.image2 = pg.transform.scale(pg.image.load(Path(c.HOME_DIR, "assets", "laser_2.png")), (20, 100))
		self.image3 = pg.transform.scale(pg.image.load(Path(c.HOME_DIR, "assets", "laser3.png")), (20, 100))
		self.image.blit(self.image, (0,0), special_flags=pg.BLEND_RGBA_MULT | pg.BLEND_ADD)
		self.image2.blit(self.image2, (0,0), special_flags=pg.BLEND_RGBA_MULT | pg.BLEND_ADD)
		self.image3.blit(self.image3, (0,0), special_flags=pg.BLEND_RGBA_SUB | pg.BLEND_RGB_MAX)
		self.bullet = PlayerBullet(self.game, self.rect.midtop, self.image, velocity=(0, -2000))

		if self.fire_timer > 0:
			return
		if self.rect.y - self.bullet.rect.y < 0:
			self.bullet.kill()

		pg.mixer.Sound(f'{c.HOME_DIR}/assets/audio/lasercont.wav').play()
		self.fire_timer = self.fire_cooldown
		self.game.player_bullets.add(self.bullet)
		self.game.all_sprites.add(self.bullet)

	def shoot_normal(self):
		bullet = PlayerBullet(self.game, self.rect.midtop, velocity=(0, -800))
		if self.fire_timer > 0:
			return
		if self.rect.y - bullet.rect.y < 0:
			bullet.kill()
		pg.mixer.Sound(f'{c.HOME_DIR}/assets/audio/lasersound2.wav').play()
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
		pg.mixer.Sound(f'{c.HOME_DIR}/assets/audio/lasersound.wav').play()
		self.fire_timer = self.fire_cooldown
		for pos, velocity in bullet_data:
			if self.pos.y + 20 < 0:
				bullet.kill()
			bullet = PlayerBullet(self.game, pos, velocity=velocity)
			self.game.player_bullets.add(bullet)
			self.game.all_sprites.add(bullet)

	def hit(self):
		if self.shield_active == False:
			self.flash_timer = 0.05
			if self.invincible_timer > 0:
				return
			pg.mixer.Sound(f'{c.HOME_DIR}/assets/audio/clink.wav').play()
			self.lives -= 1
			self.invincible_timer = 2.0
			for _ in range(100):
				particle = Particle(self.game, self.rect.center)
				self.game.effects.add(particle)
				self.game.all_sprites.add(particle)
		else:
			pg.mixer.Sound(f"{c.HOME_DIR}/assets/audio/ding.mp3").play()
			if self.lives <= 0:
				explosion_sound = f'{c.HOME_DIR}/assets/explosion1-long.wav'
				pg.mixer.Sound(explosion_sound).play()
				explosion = Explosion(self.game, self.rect.center)
				self.game.effects.add(explosion)
				self.game.all_sprites.add(explosion)
				for _ in range(15000):
					particle = Particle(self.game, self.rect.center)
					self.game.effects.add(particle)
					self.game.all_sprites.add(particle)
				self.alive = False
				self.game.game_over = True
				self.kill()

	def apply_powerup(self, kind):
		if kind == "spread":
			self.shoot_mode = "spread"
			self.power_timer = 12.0
		if kind == "speed":
			self.speed = 700
			self.power_timer = 12.0
		if kind == "laser":
			self.fire_cooldown2 = 0.01
			self.power_timer = 12.0
		if kind == "health":
			self.lives += 3
		if kind == "cannon":
			self.power_timer = 12.0
			self.fire_cooldown = 0.01
		if kind == "shield":
			self.power_timer = 12.0
			self.shield = True
			self.shield_amount = self.game.level.player_shield_amount

	def shoot_vulcan(self, dt):
		if self.vulcan_timer > 0:
			return

		self.vulcan_timer = self.vulcan_cooldown
		self.vulcan_counter += 1

		muzzle = self.get_vulcan_muzzle()
		direction = self.get_mouse_aim_direction(muzzle)

		# Tiny random spread makes it feel mechanical and violent.
		direction = direction.rotate(random.uniform(-3.5, 3.5))

		bullet_speed = 1450
		velocity = direction * bullet_speed

		tracer = self.vulcan_counter % 5 == 0

		bullet = VulcanBullet(
			self.game,
			muzzle,
			velocity,
			tracer=tracer,
		)

		self.game.player_bullets.add(bullet)
		self.game.all_sprites.add(bullet)

		self.spawn_vulcan_fx(muzzle, direction)
		self.play_vulcan_sound()

	def get_vulcan_muzzle(self):
		# Alternates between left and right barrel.
		self.vulcan_side *= -1

		x_offset = 9 * self.vulcan_side
		y_offset = -36

		return pg.Vector2(
			self.rect.centerx + x_offset,
			self.rect.centery + y_offset,
		)

	def get_mouse_aim_direction(self, muzzle):
		mx, my = pg.mouse.get_pos()
		target = pg.Vector2(mx, my)

		direction = target - muzzle

		if direction.length_squared() == 0:
			return pg.Vector2(0, -1)

		return direction.normalize()

	def spawn_vulcan_fx(self, muzzle, direction):
		flash = MuzzleFlash(self.game, muzzle, direction)
		self.game.effects.add(flash)
		self.game.all_sprites.add(flash)

		for _ in range(4):
			spark = VulcanSpark(self.game, muzzle, direction)
			self.game.effects.add(spark)
			self.game.all_sprites.add(spark)

		# Shell ejects sideways from the opposite side of the active barrel.
		shell_side = -self.vulcan_side

		if random.random() < 0.75:
			shell = ShellCasing(self.game, muzzle, shell_side)
			self.game.effects.add(shell)
			self.game.all_sprites.add(shell)

	def play_vulcan_sound(self):
		if self.vulcan_sound_timer > 0:
			return

		self.vulcan_sound_timer = self.vulcan_sound_delay

		if hasattr(self.game, "play_sound"):
			self.game.play_sound(self.minigun_sound, 0.11)
		else:
			self.minigun_sound.play()

	def update(self, dt):
		keys = pg.key.get_pressed()
		mouse = pg.mouse.get_pressed()
		mx, my = pg.mouse.get_pos()
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
		if keys[pg.K_LCTRL]:
			self.shoot_railgun()
		if keys[pg.K_SPACE] or mouse[0] == 1:
			if self.shoot_mode == "spread":
				self.shoot_spread()
			elif self.shoot_mode == "cannon":
				self.shoot_railgun()
			else:
				self.shoot_normal()
		if keys[pg.K_LSHIFT]:
			self.speed = c.PLAYER_FOCUS_SPEED
		if not keys[pg.K_LSHIFT]:
			self.speed = c.PLAYER_SPEED
		if keys[pg.K_LALT]:
			self.shield_active = True
		if not keys[pg.K_LALT]:
			self.shield_active = False
		if mouse[2] == 1 or mouse[1] == 1:
			self.shoot_vulcan(dt)
			self.vulcan_timer -= dt
			self.vulcan_sound_timer -= dt

		# if keys[pg.K_LCTRL]:
		#	self.shoot_spread()

		if keys[pg.K_ESCAPE]:
			pg.quit()
		# For debugging
		if keys[pg.K_F1]:
			self.game.debug = not self.game.debug
		if keys[pg.K_F2]:
			self.game.show_hitboxes = not self.game.show_hitboxes
		if keys[pg.K_F3]:
			self.game.show_collisions = not self.game.show_collisions
		if keys[pg.K_F4]:
			self.game.show_powerups = not self.game.show_powerups
		if keys[pg.K_F5]:
			self.game.show_enemies = not self.game.show_enemies
		if keys[pg.K_F6]:
			self.game.boss.destroy()
		if keys[pg.K_F7]:
			print(*self.game.bosses)
			self.game.bosses.clear()
			c.BOSS_TIME = False
			c.BOSS_SPAWN_DELAY = 5.0
		if keys[pg.K_F8]:
			from entities.boss import Boss
			self.game.boss = {}
			self.game.boss = Boss(self.game, (random.randrange(0, 1920), -100))
			c.BOSS_TIME = True
			c.BOSS_SPAWN_DELAY = 0
			#self.game.boss = self.game.boss_spawn(name="Bane", lvl=1, image=c.BOSS[1].get("boss_image"), hp=c.BOSS[1].get("hp"))
			self.game.boss_group.add(self.boss)
			self.game.enemies.add(self.boss)
			self.all_sprites.add(self.boss)
		if keys[pg.K_F9]:
			powerup = PowerUp(self.game, (random.randrange(0, 1920), 0), kind=random.choice(["health", "speed", "spread", "laser", "cannon", "shield"]))
			self.game.powerups.add(powerup)
			self.game.all_sprites.add(powerup)
		if keys[pg.K_F11]:
			self.alive = False
		if keys[pg.K_F10]:
			c.BOSS_TIME = True

		if self.power_timer > 0:
			self.power_timer -= dt

		if self.power_timer <= 0:
			self.shoot_mode = "normal"
			self.shield = False
			self.speed = c.PLAYER_SPEED
			self.fire_cooldown2 = 0.08
		self.thruster_timer -= dt

		if self.thruster_timer <= 0:
			self.thruster_timer = 0.012

			engine_left = (self.rect.centerx - 10, self.rect.centery + 42)
			engine_right = (self.rect.centerx + 10, self.rect.centery + 42)
			for engine_pos in [engine_left, engine_right]:
				# hot core
				for _ in range(8):
					particle = ThrusterParticle(
						self.game,
						engine_pos,
						direction=(0, 1),
						color=(0, 0,255),
						speed_range=(280, 520),
						size_range=(1, 5),
						life_range=(0.12, 0.46),
						spread=12
					)
					self.game.effects.add(particle)
					self.game.all_sprites.add(particle)

				# purple/blue outer flame
				for _ in range(8):
					particle = ThrusterParticle(
						self.game,
						engine_pos,
						direction=(0, 1),
						color=(100, 180, 255),
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
						size_range=(2, 6),
						life_range=(0.12, 0.42),
						spread=15
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
