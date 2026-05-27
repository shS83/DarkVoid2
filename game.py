import random
from pygame import mixer
import pygame as pg
from entities.player import Player
from entities.boss import Boss
from entities.enemy import Enemy
from entities.star import Star
from ui.hud import HUD
from entities.asteroid import Meteor
# from core.hs_module import HighScore
from entities.level import Level
from entities.events import Event
from pathlib import Path
from entities.shield import Shield
import config as c
level = Level()

def mixing():
	mixer.init()
	tunes = ["1000 Handz - Reps.mp3", "1000 Handz - Announcement.mp3", "1000 Handz - No Option.mp3",
	         "Colorcast - Coffee Break.mp3", "Colorcast - Drown.mp3", "Colorcast - Need.mp3",
	         "Jahzzar - Forest Pan.mp3", "Jahzzar - Pink Fluid.mp3", "Lightning Traveler - Celestial Drift.mp3",
	         "Lightning Traveler - Eclipse Horizon.mp3", "Lightning Traveler - Event Horizon.mp3",
	         "Lightning Traveler - Lunar Echo.mp3", "Ov Moi Omm - The Dictator’s Transmission (YSMHB).mp3"]
	mixer.music.load(Path(c.HOME_DIR, "assets", "audio", f"{random.choice(tunes)}"))
	mixer.music.play(-1)
	mixer.init(48000, -16, 2, 4096)
	mixer.music.set_volume(0.2)
	mixer.set_num_channels(32)

class Game:
	def __init__(self):
		pg.init()
		mixing()
		self.level = Level()
		self.level.stage = 1
		c.event = Event.INITIATION
		c.HOME_DIR = Path(__file__).parent.absolute()
		print(c.HOME_DIR)
		self.bosses=[]
		self.screen = pg.display.set_mode((c.WIDTH, c.HEIGHT), pg.SRCALPHA, 32)
		self.clock = pg.time.Clock()
		self.dt = self.clock.tick(60) / 1000
		self.running = True
		self.enemies = pg.sprite.Group()
		self.boss_group = pg.sprite.Group()
		self.enemy_bullets = pg.sprite.Group()
		self.texts = pg.sprite.Group()
		self.powerups = pg.sprite.Group()
		self.effects = pg.sprite.Group()
		self.asteroids = pg.sprite.Group()
		self.boss = None
		self.boss_time = False
		self.boss_timer = level.boss_timer
		self.level_timer = 0
		self.boss_spawn_delay = c.BOSS_SPAWN_DELAY
		self.boss_spawned_this_level = False
		self.boss_max_y = 160
		self.score = 0
		self.hud = HUD(self)
		self.effects = pg.sprite.Group()
		self.explosion_frames = []
		self.boss_explosion_frames = []
		self.enemy_spawn_timer = 0
		self.enemy_spawn_delay = random.uniform(1.5, 10.0)
		self.asteroids = pg.sprite.Group()
		self.asteroid_spawn_timer = 0
		self.asteroid_spawn_delay = random.uniform(5, 20)
		self.rock_images = []
		for i in range(1, 5):
			img = pg.image.load(Path(c.HOME_DIR, "assets", "rocks", f"rock_{i}.png")).convert_alpha()
			self.rock_images.append(img)
		for i in range(1, 32):
			img = pg.image.load(Path(c.HOME_DIR, "assets", "explosions", f"exp_{i}.png")).convert_alpha()
			img = pg.transform.scale(img, (320, 320))
			self.explosion_frames.append(img)
		for i in range(1, 32):
			img = pg.image.load(Path(c.HOME_DIR, "assets", "explosions", f"exp_{i}.png")).convert_alpha()
			img = pg.transform.scale(img, (640, 640))
			self.boss_explosion_frames.append(img)
		self.background = pg.image.load(Path(c.HOME_DIR, "assets", "backgrounds", "space_background.png")).convert()
		self.background = pg.transform.scale(self.background, (c.WIDTH, c.HEIGHT))
		self.direction = 1
		self.px = c.WIDTH // 2
		self.py = -42
		self.dt = 0
		self.all_sprites = pg.sprite.LayeredUpdates()
		self.next_level_angle = 360
		self.next_level_scale = 5
		self.text_alpha = 255
		self.banner = pg.Surface((400, 300), pg.SRCALPHA)
		self.next_level_backdrop_alpha = 20
		self.next_level_backdrop_scale = 0.1
		self.overlay_timer = 2000
		self.game_over_font = pg.font.Font(f'{c.HOME_DIR}/assets/fonts/JetBrainsMonoNerdFont-SemiBold.ttf', 72)
		self.rotated_text = pg.Surface((400, 100), pg.SRCALPHA)
		self.next_level_text = self.game_over_font.render("Next Stage", True, (200, 200, 255))
		self.next_level_backdrop_alpha = 235
		self.next_level_backdrop_scale = 0.1
		self.game_over = False
		self.game_over_angle = 0
		self.game_over_scale = 0.1
		self.game_over_scale_dir = 1
		self.game_over_backdrop_scale = 0.1
		self.game_over_backdrop_alpha = 235
		self.text_alpha = 255
		self.game_over_text = self.game_over_font.render("YOU FELLED", True, (255, 40, 40))
		self.player = Player(self, (c.WIDTH // 2, c.HEIGHT - 90))
		self.all_sprites.add(self.player)
		self.player_bullets = pg.sprite.Group()
		self.stars = pg.sprite.Group()

		for _ in range(200):
			self.stars.add(Star())

	def play_sound(self, sound, volume=1.0):
		channel = pg.mixer.find_channel(True)

		if channel:
			sound.set_volume(volume)
			channel.play(sound)

	def spawn_asteroid(self):
		x = random.randint(-40, c.WIDTH + 40)
		y = random.randint(-40, c.HEIGHT + 40)

		asteroid = Meteor(self, (x, y))

		self.asteroids.add(asteroid)
		self.all_sprites.add(asteroid)

	def spawn_rocks(self):
		for _ in range(8):
			asteroid = Meteor(self, (random.randint(0, c.WIDTH), random.randrange(-150, -50)))
			x = random.randint(50, c.WIDTH - 50)
			y = -100

			test_rect = pg.Rect(0, 0, 64, 64)
			test_rect.center = (x, y)

			overlap = False

			for asteroid in self.asteroids:
				if test_rect.colliderect(asteroid.rect.inflate(20, 20)):
					overlap = True
				if self.player.rect.colliderect(asteroid.rect) and not self.player.invincible_timer > 0:
					if not self.player.shield_active:
						self.player.hit()
					else:
						pg.mixer.Sound(f"{c.HOME_DIR}/assets/ding.mp3").play()
					break

			if not overlap:
				asteroid = Meteor(self, (x, y))
				self.asteroids.add(asteroid)
				self.all_sprites.add(asteroid)
				return


	def spawn_enemy(self):

		if random.random() < 0.15:
			self.spawn_rocks()

		for b in self.bosses:
			b.update(1/ 60/1000)

		for _ in range(20):  # try 20 times
			x = random.randint(50, c.WIDTH - 50)
			y = -60

			test_rect = pg.Rect(0, 0, 64, 64)
			test_rect.center = (x, y)

			overlap = False

			for enemy in self.enemies:
				if test_rect.colliderect(enemy.rect.inflate(20, 20)):
					overlap = True
				if self.player.rect.colliderect(enemy.rect) and not self.player.invincible_timer > 0:
					if not self.player.shield_active:
						self.player.hit()
					else:
						pg.mixer.Sound(f"{c.HOME_DIR}/assets/ding.mp3").play()
					break

			if not overlap:
				enemy = Enemy(self, (x, y))
				self.enemies.add(enemy)
				self.all_sprites.add(enemy)
				return

	def boss_spawn(self, name="Unnamed", lvl=1, image=None, hp=1000, pos=None):
		if self.boss is not None:
			return

		c.BOSS_TIME = True

		if pos is None:
			pos = (c.WIDTH // 2, -160)

		self.boss = Boss(
			self,
			name=name,
			pos=pos,
			image=image,
			hp=hp,
			lvl=lvl
		)

		self.enemies.add(self.boss)
		self.all_sprites.add(self.boss)

		if level.stage == 3:
			print("nextlevel shite")
			if not level.next_boss_candidate or level.nextboss:
				c.NEXTBOSS = c.BOSS.pop(0)
			self.boss = Boss(self, c.NEXTBOSS.get("pos"), (0, -1))
			self.boss.image = pg.transform.smoothscale(pg.image.load(
				c.NEXTBOSS.get("image", f"{c.HOME_DIR}/assets/ships/bosses/foobarhead1.png")).convert_alpha(), (240, 240))
			self.boss_hp = level.boss_hp
			self.boss_time = c.BOSS_TIME
			self.boss_group.add(self.boss)
			self.enemies.add(self.boss)
			self.all_sprites.add(self.boss)
			self.boss_spawned_this_level = True

		if level.stage == 2:
			print("kakkone on ykköne")
			if not level.next_boss_candidate or level.nextboss:
				c.NEXTBOSS = c.BOSS.pop(0)
			self.boss = Boss(self, c.NEXTBOSS.get("pos"), (0, -1))
			self.boss.image = pg.image.load(
				c.NEXTBOSS.get("image", f"{c.HOME_DIR}/assets/ships/bosses/foobarhead1.png")).convert_alpha()
			self.boss_hp = level.boss_hp
			self.angle += 1
			self.boss_time = c.BOSS_TIME
			self.boss_group.add(self.boss)
			self.enemies.add(self.boss)
			self.all_sprites.add(self.boss)
			self.boss_spawned_this_level = True

		if level.stage == 1:
			print("el virgo")
			if not level.next_boss_candidate or level.nextboss:
				c.NEXTBOSS = c.BOSS.pop(0)
			self.boss = Boss(self, c.NEXTBOSS.get("pos"), (0, -1))
			self.boss.image = pg.image.load(c.NEXTBOSS.get("image", f"{c.HOME_DIR}/assets/ships/bosses/foobarhead1.png")).convert_alpha()
			self.boss_hp = level.boss_hp
			self.boss_time = c.BOSS_TIME
			self.boss_group.add(self.boss)
			self.enemies.add(self.boss)
			self.all_sprites.add(self.boss)
			self.boss_spawned_this_level = True
			print("boss created:", self.boss.pos)
			print("boss added to groups")


		if self.player.rect.colliderect(self.boss.rect) and not self.player.invincible_timer > 0:
			if not self.player.shield_active:
				self.player.hit()
			else:
				pg.mixer.Sound(f"{c.HOME_DIR}/assets/ding.mp3").play()

	def update(self, dt):
		for b in self.bosses:
			b.update(dt)
		self.enemies.update(dt)
		self.boss_group.update(dt)
		self.enemy_bullets.update(dt)
		self.player_bullets.update(dt)
		self.stars.update(dt)
		self.asteroids.update(dt)
		self.all_sprites.update(dt)

		if not c.BOSS_TIME and self.boss is None:
			self.boss_timer -= dt
			if not c.NEXTBOSS:
				self.boss_dict = c.BOSS.pop(0)
				c.NEXTBOSS = self.boss_dict.copy()

			if self.boss_timer <= 0:
				self.boss_timer = 0
				self.boss_spawn(
					name=self.boss_dict.get("name", "unknown"),
					lvl=self.level.stage,
					image=self.boss_dict.get("image", f"{c.HOME_DIR}/assets/ships/bosses/foobarhead1.png"),
					hp=self.level.boss_hp
				)
			self.level_timer += dt
			self.enemy_spawn_timer += dt
			if self.enemy_spawn_timer >= self.enemy_spawn_delay and len(self.enemies) < level.max_enemies:
				self.enemy_spawn_timer = 0
				self.enemy_spawn_delay = random.uniform(0.4, 3.0)
				self.spawn_enemy()

		self.asteroid_spawn_timer += dt
		if self.asteroid_spawn_timer >= self.asteroid_spawn_delay:
			self.asteroid_spawn_timer = 0
			self.asteroid_spawn_delay = random.uniform(0.40, 3.2)
			if len(self.asteroids) < level.max_asteroids:
				self.spawn_asteroid()
			if len(self.asteroids) < 2:
				self.spawn_rocks()

		for enemy in self.enemies:
			for bullet in self.player_bullets:
				if enemy.hitbox.colliderect(bullet.rect):
					bullet.kill()
					enemy.damage(1)
					break

		for asteroid in self.asteroids:
			for bullet in self.player_bullets:
				if asteroid.hitbox.colliderect(bullet.rect):
					bullet.kill()
					asteroid.damage(1)
					break

		for asteroid in self.asteroids:
			if asteroid.hitbox.colliderect(self.player.rect) and not self.player.invincible_timer > 0:
				self.player.hit()
				if self.player.lives <= 0:
					self.player.alive = False
					self.game_over = True
				break

		if self.player.alive and self.player.invincible_timer <= 0:
			for bullet in self.enemy_bullets:
				distance = self.player.pos.distance_to(bullet.pos)

				if distance < self.player.hitbox_radius + bullet.radius:
					bullet.kill()
					self.player.hit()
					if self.player.lives <= 0:
						self.player.alive = False
						self.game_over = True
					break

		powerup_hits = pg.sprite.spritecollide(
			self.player,
			self.powerups,
			True
		)

		for powerup in powerup_hits:
			self.player.apply_powerup(powerup.kind)

		if (
				self.level_timer >= self.boss_spawn_delay
				and not self.boss_spawned_this_level
				and self.boss is None
		):
			print("bossi spawnautumassa")
			self.bosses.clear()
			if level.next_boss_candidate is None:
				print("nöössi")
			boss_dict = c.BOSS.pop(0)
			print(f"you're fighting {boss_dict.get("name")}")
			self.boss_spawn(name=boss_dict.get("name", "unknown"), lvl=level.stage,
							image=boss_dict.get("image", f"{c.HOME_DIR}/assets/ships/bosses/foobarhead1.png"), hp=level.boss_hp)
		if not self.player.alive:
			self.game_over = True

		if self.game_over:
			self.game_over_scale += self.game_over_scale_dir * 0.4 * dt
			self.text_alpha -= 0.3
			self.game_over_backdrop_scale += 2.8 * dt
			if self.game_over_backdrop_scale > 6:
				self.game_over_backdrop_scale = 6
			self.game_over_backdrop_alpha -= 50 * dt
			if self.game_over_backdrop_alpha < 80:
				self.game_over_backdrop_alpha = 80
			return

	def draw(self):
		self.effects.draw(self.screen)
		self.screen.blit(self.background, (0, 0))
		self.enemies.draw(self.screen)
		self.boss_group.draw(self.screen)
		self.powerups.draw(self.screen)
		self.stars.draw(self.screen)
		self.hud.draw(self.screen)
		self.asteroids.draw(self.screen)
		self.all_sprites.draw(self.screen)

		if c.Event == c.Event.PAUSE:
			pausesurface = pg.Surface((c.WIDTH, c.HEIGHT), pg.SRCALPHA)
			pausesurface.fill((0, 0, 0, 120))
			mixer.fadeout(1000)
			pausetext = self.game_over_font.render("| |", True, (255, 255, 255))
			pause_rect = pausetext.get_rect(center=(c.WIDTH // 2, c.HEIGHT // 2))

			pausesurface.blit(pausetext, pause_rect)
			self.screen.blit(pausesurface, (0, 0))

		pg.display.flip()

		if c.event == c.Event.NEXTLEVEL:
			level.next_boss_candidate = level.boss_tree.pop(0)
			self.rotated_text = pg.Surface((400, 100), pg.SRCALPHA)
			overlay = pg.Surface((c.WIDTH, c.HEIGHT), pg.SRCALPHA)
			overlay.fill((0, 0, 50, 25))
			self.screen.blit(overlay, (0, 0))
			rect_width = c.WIDTH
			rect_height = 300
			self.banner = pg.Surface((rect_width, rect_height), pg.SRCALPHA)
			self.banner.fill((255, 255, 255, int(min(0, max(self.next_level_backdrop_alpha//2, 255)))))
			if self.text_alpha > 1:
				self.next_level_backdrop_alpha += 0.01
			elif self.text_alpha < 100:
				self.next_level_backdrop_alpha -= 1

			banner_rect = self.banner.get_rect(
				center=(c.WIDTH // 2, c.HEIGHT // 2)
			)
			levelup_font = pg.font.Font(f'{c.HOME_DIR}/assets/fonts/JetBrainsMonoNerdFont-SemiBold.ttf', 72)
			self.banner.set_alpha(20)
			self.screen.blit(self.banner, banner_rect)

			self.rotated_text.blit(next_level_text := levelup_font.render("Next Stage", True, (0, 0, 255)), (c.WIDTH // 2, c.HEIGHT // 2))

			clock = pg.time.Clock()
			self.dt = clock.tick(60) / 1000
			self.next_level_scale -= self.dt * 2.5

			rect = self.rotated_text.get_rect(
				center=(self.rotated_text.get_width() // 2, self.rotated_text.get_height() // 2)
			)
			pg.draw.rect(self.screen, self.rotated_text.get_bounding_rect(), (255, 0, 0, 255))
			rotated_text = pg.transform.rotozoom(
				self.next_level_text,
				self.next_level_angle,
				self.next_level_scale
			)
			self.text_alpha -= 0.05
			self.rotated_text.set_alpha(self.text_alpha)
			self.next_level_angle += self.dt
			self.screen.blit(rotated_text, rect)
		pg.display.flip()

		if self.game_over:
			# Screen darkening
			overlay = pg.Surface((c.WIDTH, c.HEIGHT), pg.SRCALPHA)
			overlay.fill((0, 0, 0, 25))
			self.screen.blit(overlay, (0, 0))

			# Expanding dark rectangle
			rect_width = c.WIDTH
			rect_height = 300

			banner = pg.Surface((rect_width, rect_height), pg.SRCALPHA)

			banner.fill((0, 0, 0, int(self.game_over_backdrop_alpha)))
			if self.text_alpha > 1:
				self.game_over_backdrop_alpha += 0.1
			elif self.text_alpha > 100:
				self.game_over_backdrop_alpha -= 1

			banner_rect = banner.get_rect(
				center=(c.WIDTH // 2, c.HEIGHT // 2)
			)

			self.screen.blit(banner, banner_rect)

			rotated_text = pg.transform.rotozoom(
				self.game_over_text,
				self.game_over_angle,
				self.game_over_scale
			)
			rotated_text.set_alpha(self.text_alpha)
			rect = rotated_text.get_rect(
				center=(c.WIDTH // 2, c.HEIGHT // 2)
			)

			self.screen.blit(rotated_text, rect)
		pg.display.flip()

	def run(self):
		while self.running:
			dt = self.clock.tick(c.FPS) / 1000

			for event in pg.event.get():
				if event.type == pg.QUIT:
					self.running = False
				if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
					self.running = False
				if event.type == pg.KEYDOWN and event.key == pg.K_PAUSE:
					if c.Event == c.Event.PAUSE:
						mixer.music.play(-1)
						c.Event = c.Event.PLAYING
					elif c.Event != c.Event.PAUSE:
						c.Event = c.Event.PAUSE
				if event.type == pg.KEYDOWN and event.key == pg.K_LSHIFT:
					self.player.speed = self.player.focus_speed
				if self.player.shield is True and event.type == pg.KEYDOWN and event.key == pg.K_LALT:

					self.player.shield_active = True
					shield = Shield(self, self.player)

					self.effects.add(shield)
					self.all_sprites.add(shield)
					self.player.shield_amount -= 1

				if event.type == pg.KEYUP and event.key == pg.K_LSHIFT:
					self.player.speed = c.PLAYER_SPEED

				if event.type == pg.KEYUP and event.key == pg.K_LALT:
					self.player.shield_active = False


			if c.event != c.Event.PAUSE:
				self.update(dt)
			self.draw()


	pg.quit()
	mixer.quit()

if __name__ == "__main__":
	game = Game()
	game.run()
