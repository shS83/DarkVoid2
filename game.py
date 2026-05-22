from pygame import mixer
import pygame as pg
import config as c
from entities.events import Event
from entities.player import Player
from entities.boss import Boss
from entities.enemy import Enemy
from entities.star import Star
from ui.hud import HUD
from entities.asteroid import Meteor
from entities.level import *
from core.hs_module import HighScore
from entities.level import Level
from pathlib import Path
c.Level = Level()

def mixing():
	mixer.init()
	tunes = ["1000 Handz - Reps.mp3", "1000 Handz - Announcement.mp3", "1000 Handz - No Option.mp3",
	         "Colorcast - Coffee Break.mp3", "Colorcast - Drown.mp3", "Colorcast - Need.mp3",
	         "Jahzzar - Forest Pan.mp3", "Jahzzar - Pink Fluid.mp3", "Lightning Traveler - Celestial Drift.mp3",
	         "Lightning Traveler - Eclipse Horizon.mp3", "Lightning Traveler - Event Horizon.mp3",
	         "Lightning Traveler - Lunar Echo.mp3", "Ov Moi Omm - The Dictator’s Transmission (YSMHB).mp3"]
	mixer.music.load(Path(c.HOME_DIR, "assets", f"{random.choice(tunes)}"))
	mixer.music.play(-1)
	mixer.init(48000, -16, 2, 4096)
	mixer.music.set_volume(0.2)
	mixer.set_num_channels(32)


class Game:
	def __init__(self):
		pg.init()
		mixing()
		self.enemies = pg.sprite.Group()
		self.boss_group = pg.sprite.Group()
		self.enemy_bullets = pg.sprite.Group()
		self.texts = pg.sprite.Group()
		self.powerups = pg.sprite.Group()
		self.effects = pg.sprite.Group()
		self.asteroids = pg.sprite.Group()
		if c.Event == c.Event.NEXTLEVEL:
			self.boss = Boss(self, (c.WIDTH // 2, -300))
			self.boss.image = pg.transform.scale(pg.image.load(Path(c.HOME_DIR, "assets", "foobarhead1.png")), (160, 160))
			self.boss_time = c.BOSS_TIME
			self.boss_group.add(self.boss)
		else:
			self.boss = None
			self.boss_time = False
			self.boss_image = None
		self.boss_timer = c.level.boss_timer
		self.boss_max_y = 160
		self.score = 0
		self.hud = HUD(self)
		self.screen = pg.display.set_mode((c.WIDTH, c.HEIGHT), pg.SRCALPHA, 32)
		self.clock = pg.time.Clock()
		self.dt = self.clock.tick(60) / 1000
		self.running = True
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
			img = pg.image.load(Path(c.HOME_DIR, "assets", f"rock_{i}.png")).convert_alpha()
			self.rock_images.append(img)
		for i in range(1, 32):
			img = pg.image.load(Path(c.HOME_DIR, "assets", f"exp_{i}.png")).convert_alpha()
			img = pg.transform.scale(img, (320, 320))
			self.explosion_frames.append(img)
		for i in range(1, 32):
			img = pg.image.load(Path(c.HOME_DIR, "assets", f"exp_{i}.png")).convert_alpha()
			img = pg.transform.scale(img, (640, 640))
			self.boss_explosion_frames.append(img)
		self.background = pg.image.load(Path(c.HOME_DIR, "assets", "space_background.png")).convert()
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
		self.overlay_timer = 500
		self.game_over_font = pg.font.SysFont(f'{c.HOME_DIR}/assets/JetBrainsMonoNerdFont-SemiBold.ttf', 72)
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
		if self.boss_timer <= 0 and not self.boss:
			self.boss = Boss(self, (c.WIDTH // 2, -80))
			self.enemies.add(self.boss)
			self.all_sprites.add(self.boss)
		self.stars = pg.sprite.Group()

		for _ in range(200):
			self.stars.add(Star())

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
					self.player.hit()
					break

			if not overlap:
				asteroid = Meteor(self, (x, y))
				self.asteroids.add(asteroid)
				self.all_sprites.add(asteroid)
				return

	def spawn_enemy(self):
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
					self.player.hit()
					break

			if not overlap:
				enemy = Enemy(self, (x, y))
				self.enemies.add(enemy)
				self.all_sprites.add(enemy)
				return

	def boss_spawn(self):
		c.BOSS_TIME = True
		x = c.WIDTH // 2
		y = -300

		if not self.boss:
			self.boss = Boss(self, (x, y))

			self.enemies.add(self.boss)
			self.all_sprites.add(self.boss)

		if self.player.rect.colliderect(self.boss.rect) and not self.player.invincible_timer > 0:
			self.player.hit()
	if c.Event != c.Event.PAUSE:
		def update(self, dt):
			if not c.BOSS_TIME:
				self.boss_timer -= dt * 75
			self.stars.update(dt)
			self.asteroids.update(dt)
			self.all_sprites.update(dt)
			if not c.BOSS_TIME:
				self.enemy_spawn_timer += dt

			if not c.BOSS_TIME or self.boss_timer >= 500:
				if self.enemy_spawn_timer >= self.enemy_spawn_delay:
					self.enemy_spawn_timer = 0
					self.enemy_spawn_delay = random.uniform(0.4, 3.6)
					self.spawn_enemy()

			self.asteroid_spawn_timer += dt

			if self.asteroid_spawn_timer >= self.asteroid_spawn_delay:
				self.asteroid_spawn_timer = 0
				self.asteroid_spawn_delay = random.uniform(0.40, 3.2)
				if len(self.asteroids) < c.level.max_asteroids:
					self.spawn_asteroid()

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
					break
				# elif asteroid.hitbox.colliderect(asteroid.rect):
				# 	asteroid.damage(1)
				# 	break
			if self.boss_timer < 1:
				self.boss_timer = 0
				self.boss_spawn()

			if self.player.alive and self.player.invincible_timer <= 0:
				for bullet in self.enemy_bullets:
					distance = self.player.pos.distance_to(bullet.pos)

					if distance < self.player.hitbox_radius + bullet.radius:
						bullet.kill()
						self.player.hit()
						break

			powerup_hits = pg.sprite.spritecollide(
				self.player,
				self.powerups,
				True
			)

			for powerup in powerup_hits:
				self.player.apply_powerup(powerup.kind)

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
		if c.Event == c.Event.PAUSE:
				pausesurface = pg.Surface((c.WIDTH, c.HEIGHT), pg.SRCALPHA, 32)
				pausesurface.fill((0, 0, 0, 60))
				pausetext = self.game_over_font.render("| |", True, (255, 255, 255))
				pausesurface.blit(pausetext, (c.WIDTH // 2, c.HEIGHT // 2))
				self.screen.blit(pausesurface, (0, 0))
				mixer.music.fadeout(1000)
				pg.display.flip()
		else:
				def draw(self):
					self.screen.blit(self.background, (0, 0))
					self.powerups.draw(self.screen)
					self.stars.draw(self.screen)
					self.hud.draw(self.screen)
					self.asteroids.draw(self.screen)
					self.all_sprites.draw(self.screen)

					if c.Event == c.Event.NEXTLEVEL:
						# Screen whitening
						if self.overlay_timer > 0:
							self.overlay_timer -= self.dt / 2
						else:
							self.overlay_timer = 0

						if self.overlay_timer > 0:
							self.rotated_text = pg.Surface((400, 100), pg.SRCALPHA)
							overlay = pg.Surface((c.WIDTH, c.HEIGHT), pg.SRCALPHA)
							overlay.fill((0, 0, 50, 25))
							self.screen.blit(overlay, (0, 0))
							rect_width = c.WIDTH
							rect_height = 300
							self.banner = pg.Surface((rect_width, rect_height), pg.SRCALPHA)
							self.banner.fill((255, 255, 255, int(self.next_level_backdrop_alpha)-self.overlay_timer//2))
						if self.text_alpha > 1:
							self.next_level_backdrop_alpha += 0.01
						elif self.text_alpha < 100:
							self.next_level_backdrop_alpha -= 1

						banner_rect = self.banner.get_rect(
							center=(c.WIDTH // 2, c.HEIGHT // 2)
						)
						levelup_font = pg.font.SysFont(f'{c.HOME_DIR}/assets/JetBrainsMonoNerdFont-SemiBold.ttf', 72)
						self.banner.set_alpha(20)
						self.screen.blit(self.banner, banner_rect)

						self.rotated_text.blit(next_level_text := levelup_font.render("Next Stage", True, (0, 0, 255)), (c.WIDTH // 2, c.HEIGHT // 2))

						clock = pg.time.Clock()
						self.dt = clock.tick(60) / 1000
						self.next_level_scale -= self.dt / 2.5

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
						self.next_level_angle += 10 * self.dt
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
							self.game_over_backdrop_alpha += 0.01
						elif self.text_alpha < 100:
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
						c.Event = c.Event.DRUMROLL
						c.Event = c.Event.PLAYING
					elif c.Event != c.Event.PAUSE:
						c.Event = c.Event.PAUSE

			if c.Event != c.Event.PAUSE:
				self.update(dt)
				self.draw()


		scores = HighScore("John", self.score)
		scores.load_scores()
		scores.check_score(self.score)


pg.quit()
mixer.quit()

if __name__ == "__main__":
	game = Game()
	game.run()
