import random
from systems.highscores import HighScoreTable
from entities.earth import Earth
from pygame import mixer
import pygame as pg
from entities.player import Player
from entities.boss import Boss
from entities.enemy import Enemy
from entities.star import Star
from ui.hud import HUD
from entities.asteroid import Meteor
from entities.level import Level
from entities.events import Event
from pathlib import Path
from entities.shield import Shield
from systems.world_manager import MapManager
import config as c
import math

def mixing():
	mixer.init()
	tunes = [
		"1000 Handz - Reps.mp3",
		"1000 Handz - Announcement.mp3",
		"1000 Handz - No Option.mp3",
		"Colorcast - Coffee Break.mp3",
		"Colorcast - Drown.mp3",
		"Colorcast - Need.mp3",
		"Jahzzar - Forest Pan.mp3",
		"Jahzzar - Pink Fluid.mp3",
		"Lightning Traveler - Celestial Drift.mp3",
		"Lightning Traveler - Eclipse Horizon.mp3",
		"Lightning Traveler - Event Horizon.mp3",
		"Lightning Traveler - Lunar Echo.mp3",
		"Ov Moi Omm - The Dictator’s Transmission (YSMHB).mp3",
	]
	mixer.music.load(
		c.resource_path(Path(c.HOME_DIR, "assets", "audio", random.choice(tunes)))
	)
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
		c.BOSS = c.make_boss_list()
		c.BOSS_TIME = False
		self.map_manager = None
		self.world_phase = "space"
		self.world_timer = 0
		self.fade_alpha = 0
		self.stage_banner_text = None
		self.bosses = []
		self.highscores = HighScoreTable(Path(c.HOME_DIR, "highscores.json"))
		self.score_saved = False
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
		self.boss_timer = self.level.boss_timer
		c.BOSS_TIMER = self.boss_timer
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
		self.earth = Earth()
		self.earth_updates = False
		self.rock_images = []
		for i in range(1, 5):
			img = pg.image.load(
				c.resource_path(Path(c.HOME_DIR, "assets", "rocks", f"rock_{i}.png"))
			).convert_alpha()
			self.rock_images.append(img)
		for i in range(1, 32):
			img = pg.image.load(
				c.resource_path(
					Path(c.HOME_DIR, "assets", "explosions", f"exp_{i}.png")
				)
			).convert_alpha()
			img = pg.transform.scale(img, (320, 320))
			self.explosion_frames.append(img)
		for i in range(1, 32):
			img = pg.image.load(
				c.resource_path(
					Path(c.HOME_DIR, "assets", "explosions", f"exp_{i}.png")
				)
			).convert_alpha()
			img = pg.transform.scale(img, (640, 640))
			self.boss_explosion_frames.append(img)
		self.background = pg.image.load(
			c.resource_path(
				Path(c.HOME_DIR, "assets", "backgrounds", "space_background.png")
			)
		).convert()
		self.background = pg.transform.scale(self.background, (c.WIDTH, c.HEIGHT))
		self.direction = 1
		self.px = c.WIDTH // 2
		self.py = -42
		self.dt = 0
		self.all_sprites = pg.sprite.LayeredUpdates()
		self.game_over_font = pg.font.Font(
			Path(c.HOME_DIR, "assets", "fonts", "JetBrainsMonoNerdFont-SemiBold.ttf"),
			96,
		)
		self.stage_font = pg.font.Font(
			Path(c.HOME_DIR, "assets", "fonts", "JetBrainsMonoNerdFont-SemiBold.ttf"),
			96,
		)
		self.stage_banner_duration = 2.4
		self.final_banner_timer = 20
		self.stage_banner_timer = self.stage_banner_duration
		self.stage_banner_stage = self.level.stage
		self.boss_hp = 300
		self.boss_dict = {}
		self.game_over = False
		self.game_over_timer = 0
		self.gameoversound_played = False
		self.show_highscores = False
		self.victory = False
		self.nerd_font = pg.font.Font(
			Path(c.HOME_DIR, "assets", "fonts", "MonaspiceXeNerdFontPropo-Light.otf"),
			128,
		)
		self.medium_nerd = pg.font.Font(
			Path(c.HOME_DIR, "assets", "fonts", "MonaspiceXeNerdFontPropo-Light.otf"),
			56,
		)
		self.small_nerd = pg.font.Font(
			Path(c.HOME_DIR, "assets", "fonts", "MonaspiceXeNerdFontPropo-Light.otf"),
			20,
		)
		self.tiny_nerd = pg.font.Font(
			Path(c.HOME_DIR, "assets", "fonts", "MonaspiceXeNerdFontPropo-Light.otf"),
			16,
		)
		self.game_over_text = self.nerd_font.render("YOU DIED", True, (255, 40, 40))
		self.player = Player(self, (c.WIDTH // 2, c.HEIGHT - 90))
		self.all_sprites.add(self.player)
		self.player_bullets = pg.sprite.Group()
		self.stars = pg.sprite.Group()
		self.killed_by = None
		self.entering_highscore = False
		self.highscore_name = ""
		self.highscore_saved = False
		self.max_name_length = 12
		self.ending_active = False
		self.ending_timer = 0
		self.highscore_delay = 5
		self.ending_active = False
		self.ending_timer = 0
		self.highscore_sequence_started = False
		self.victory = False
		self.show_highscores = False
		self.entering_highscore = False
		self.highscore_sequence_started = False
		self.restart_requested = False
		self.transition_ship_start = None

		for _ in range(200):
			self.stars.add(Star())

	@staticmethod
	def play_sound(sound, volume=1.0):
		channel = pg.mixer.find_channel(True)

		if channel:
			sound.set_volume(volume)
			channel.play(sound)

	def start_world_transition(self):
		self.world_phase = "boss_explosion"
		self.world_timer = 0
		self.fade_alpha = 0
		self.stage_banner_text = None
		self.earth = None
		self.transition_ship_start = pg.Vector2(self.player.rect.center)
		self.player.pos = self.transition_ship_start.copy()

		for group in [
			self.enemies,
			self.asteroids,
			self.enemy_bullets,
			self.player_bullets,
			self.powerups,
		]:
			for sprite in list(group):
				sprite.kill()

	def set_transition_player_visual(self, center, scale, angle):
		width = max(1, int(self.player.original_image.get_width() * scale))
		height = max(1, int(self.player.original_image.get_height() * scale))

		image = pg.transform.smoothscale(self.player.original_image, (width, height))
		self.player.image = pg.transform.rotozoom(image, angle, 1)
		self.player.rect = self.player.image.get_rect(center=center)
		self.player.pos = pg.Vector2(center)

	def update_world_transition(self, dt):
		# self.player.image = self.player.base_image
		self.world_timer += dt

		if self.world_phase == "boss_explosion":
			self.effects.update(dt)

			if self.world_timer >= 2.0:
				self.earth = Earth()
				self.stage_banner_text = "ADVANCING TO TERRAIN"
				self.stage_banner_timer = 1.4
				self.world_phase = "earth_enter"
				self.world_timer = 0

			return

		if self.world_phase == "earth_enter":
			self.earth.update(dt)

			if self.earth.rect.centery >= c.HEIGHT // 2 - 2:
				self.stage_banner_timer = 0
				self.stage_banner_text = None
				self.world_phase = "ship_grow"
				self.world_timer = 0

		elif self.world_phase == "ship_grow":
			t = min(1, self.world_timer / 0.8)
			scale = c.PLAYER_SCALE + (0.22 - c.PLAYER_SCALE) * t
			self.player.rebuild_visuals(scale, self.transition_ship_start)
			self.player.pos = self.transition_ship_start.copy()

			if t >= 1:
				self.world_phase = "ship_to_earth"
				self.world_timer = 0
				self.transition_ship_start = self.player.pos.copy()

		elif self.world_phase == "ship_to_earth":
			raw_t = min(1, self.world_timer / 2.0)
			t = raw_t * raw_t * (3 - 2 * raw_t)

			start = self.transition_ship_start
			control = pg.Vector2(c.WIDTH * 0.28, c.HEIGHT * 0.42)
			target = pg.Vector2(self.earth.rect.center)

			pos = start.lerp(control, t).lerp(control.lerp(target, t), t)
			tangent = 2 * (1 - t) * (control - start) + 2 * t * (target - control)

			angle = -math.degrees(math.atan2(tangent.y, tangent.x)) - 90
			scale = 0.22 + (0.02 - 0.22) * t

			self.set_transition_player_visual(pos, scale, angle)

			if raw_t >= 1:
				self.world_phase = "fade_out"
				self.world_timer = 0

		elif self.world_phase == "fade_out":
			t = min(1, self.world_timer / 1.0)
			self.fade_alpha = int(255 * t)

			if t >= 1:
				self.map_manager = MapManager(self)
				self.level.stage = 5
				self.player.pos = pg.Vector2(c.WIDTH // 2, c.HEIGHT - 120)
				self.player.rebuild_visuals(c.PLAYER_SCALE, self.player.pos)
				self.world_phase = "terrain_fade_in"
				self.world_timer = 0

		elif self.world_phase == "terrain_fade_in":
			raw_t = min(1, self.world_timer / 2.0)
			self.map_manager.update(dt)
			t = min(1, self.world_timer / 1.0)
			self.fade_alpha = int(255 * (1 - t))

			if raw_t >= 1:
				self.world_phase = "terrain"
				self.stage_banner_text = None
				self.stage_banner_timer = 2.0
				self.stage_banner_stage = self.level.stage
				if self.stage_banner_timer > 0:
					self.draw_stage_banner()
				self.boss_spawn_delay = c.BOSS_SPAWN_DELAY
				self.boss_spawned_this_level = False

		elif self.world_phase == "terrain":
			self.map_manager.update(dt)
			self.all_sprites.update(dt)
			self.enemy_spawn_timer += dt
			if (
					self.enemy_spawn_timer >= self.enemy_spawn_delay
					and len(self.enemies) < self.level.max_enemies
			):
				self.enemy_spawn_timer = 0
				self.enemy_spawn_delay = random.uniform(0.35, 1.7)
				self.spawn_enemy()

			if not c.BOSS_TIME and self.boss is None:
				self.level_timer += dt

				if self.level_timer >= self.boss_spawn_delay and c.BOSS:
					boss_dict = c.BOSS.pop(0)
					self.boss_spawn(
						name=boss_dict.get("name", "unknown"),
						lvl=boss_dict.get("lvl", self.level.stage),
						image=boss_dict.get("boss_image"),
						hp=boss_dict.get("boss_hp", self.level.boss_hp),
						pos=boss_dict.get("pos", (c.WIDTH // 2, -160)),
					)
			print("terrain", self.level_timer, self.boss_spawn_delay, len(c.BOSS), c.BOSS_TIME, self.boss)

			self.handle_collisions()

	def damage_player(self, killer="Hermaeus Mora"):
		if not self.player.alive:
			self.player.killer = killer
			return

		if hasattr(self.player, "receive_hit"):
			self.player.receive_hit(killer=self.player.killer)
		else:
			self.player.hit(killer=self.player.killer)

		if self.player.lives <= 0 or not self.player.alive:
			self.player.alive = False
			self.end_game(victory=False)

			if self.highscores.is_high_score(self.score):
				self.entering_highscore = True
				self.highscore_name = ""
			else:
				self.highscore_saved = True

	def bullet_hits_target(self, bullet, target):
		target_hitbox = getattr(target, "hitbox", target.rect)

		if not target_hitbox.colliderect(bullet.rect):
			return False

		if hasattr(target, "mask"):
			bullet_mask = getattr(bullet, "mask", None)

			if bullet_mask is None:
				bullet_mask = pg.mask.from_surface(bullet.image)

			offset = (
				bullet.rect.left - target.rect.left,
				bullet.rect.top - target.rect.top,
			)
			return target.mask.overlap(bullet_mask, offset) is not None

		return True

	def spawn_asteroid(self):
		x = random.randint(-40, c.WIDTH + 40)
		y = random.randint(-40, c.HEIGHT + 40)

		asteroid = Meteor(self, (x, y))

		self.asteroids.add(asteroid)
		self.all_sprites.add(asteroid)

	def spawn_rocks(self):
		for _ in range(8):
			asteroid = Meteor(
				self, (random.randint(0, c.WIDTH), random.randrange(-150, -50))
			)
			x = random.randint(50, c.WIDTH - 50)
			y = -100

			test_rect = pg.Rect(0, 0, 64, 64)
			test_rect.center = (x, y)

			overlap = False

			for asteroid in self.asteroids:
				if test_rect.colliderect(asteroid.rect.inflate(20, 20)):
					overlap = True
				if (
					self.player.rect.colliderect(asteroid.rect)
					and not self.player.invincible_timer > 0
				):
					self.damage_player(killer="The Rock")
					break

			if not overlap:
				asteroid = Meteor(self, (x, y))
				self.asteroids.add(asteroid)
				self.all_sprites.add(asteroid)
				return

	def spawn_enemy(self):
		if c.BOSS_TIME or self.boss is not None:
			return
		if self.level.stage < 5 and random.random() < 0.15:
			self.spawn_rocks()

		clock = pg.time.Clock()
		for b in self.bosses:
			b.update(clock.tick(60) * 0.001)

		for _ in range(20):  # try 20 times
			x = random.randint(50, c.WIDTH - 50)
			y = -60

			test_rect = pg.Rect(0, 0, 64, 64)
			test_rect.center = (x, y)

			overlap = False

			for enemy in self.enemies:
				if test_rect.colliderect(enemy.rect.inflate(20, 20)):
					overlap = True
				if (
					self.player.rect.colliderect(enemy.rect)
					and not self.player.invincible_timer > 0
				):
					self.damage_player(killer=f"Collision with {enemy.name}")
					break

			if not overlap:
				enemy = Enemy(self, (x, y), boss=False)
				self.enemies.add(enemy)
				self.all_sprites.add(enemy)
				return

	def boss_spawn(self, name="unknown", lvl=1, image=None, hp=1000, pos=None):
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
			lvl=lvl,
		)

		self.enemies.add(self.boss)
		self.all_sprites.add(self.boss)

		print(f"Boss spawned: {name}, lvl={lvl}, hp={hp}, pos={pos}")

		if (
			self.player.rect.colliderect(self.boss.rect)
			and not self.player.invincible_timer > 0
		):
			self.damage_player(killer=self.boss.name)
		return self.boss

	def update(self, dt):
		if self.world_phase != "space":
			self.update_world_transition(dt)
			self.update_stage_banner(dt)
			return

		self.stars.update(dt)
		self.all_sprites.update(dt)
		if self.player.intro_active:
			return

		if self.earth_updates:
			self.earth.update(dt)

		if self.level.stage != self.stage_banner_stage:
			self.stage_banner_stage = self.level.stage
			self.stage_banner_timer = self.stage_banner_duration
			c.event = Event.PLAYING

		if self.stage_banner_timer > 0:
			self.stage_banner_timer = max(0, self.stage_banner_timer - dt)

		if self.game_over:
			self.game_over_timer += dt

			if self.ending_active:
				self.ending_timer += dt

				if (
					self.ending_timer >= self.highscore_delay
					and not self.highscore_sequence_started
				):
					self.highscore_sequence_started = True
					self.show_highscores = True
					self.start_highscore_entry()
			return

		if not self.player.alive:
			self.end_game(victory=False)
			return

		if not c.BOSS_TIME and self.boss is None:
			self.level_timer += dt

			self.enemy_spawn_timer += dt

			if (
				self.enemy_spawn_timer >= self.enemy_spawn_delay
				and len(self.enemies) < self.level.max_enemies
			):
				self.enemy_spawn_timer = 0
				self.enemy_spawn_delay = random.uniform(0.4, 3.0)
				self.spawn_enemy()

			self.asteroid_spawn_timer += dt

			if self.asteroid_spawn_timer >= self.asteroid_spawn_delay:
				self.asteroid_spawn_timer = 0
				self.asteroid_spawn_delay = random.uniform(0.40, 3.2)

				if self.level.stage < 5 and len(self.asteroids) < self.level.max_asteroids:
					self.spawn_asteroid()

			if self.ending_active:
				self.ending_timer += dt

				if (
					self.ending_timer >= self.highscore_delay
					and not self.highscore_sequence_started
				):
					self.highscore_sequence_started = True
					self.show_highscores = True
					self.start_highscore_entry()

			if self.level_timer >= self.boss_spawn_delay and self.boss is None:
				if c.BOSS:
					boss_dict = c.BOSS.pop(0)
					self.boss_spawn(
						name=boss_dict.get("name", "unknown"),
						lvl=self.level.stage,
						image=boss_dict.get("boss_image"),
						hp=boss_dict.get("boss_hp", self.level.boss_hp),
						pos=boss_dict.get("pos", (c.WIDTH // 2, -160)),
					)

		# THIS MUST BE OUTSIDE THE if not c.BOSS_TIME BLOCK
		self.handle_collisions()

		if not self.player.alive and self.player.visible:
			self.game_over = True
			self.player.alive = False
			self.end_game(victory=False)

	def draw(self):
		if self.world_phase in ("terrain_fade_in", "terrain"):
			self.map_manager.draw(self.screen)
		else:
			self.screen.blit(self.background, (0, 0))
			self.stars.draw(self.screen)
		if self.world_phase in ("earth_enter", "ship_grow", "ship_to_earth", "fade_out"):
			self.earth.draw(self.screen)
		self.all_sprites.draw(self.screen)
		self.hud.draw(self.screen)


		if c.DEBUG:
			if self.boss is not None:
				pg.draw.rect(self.screen, (255, 0, 0), self.boss.hitbox, 3)
			pg.draw.rect(self.screen, (255, 0, 0), self.player.hitbox, 3)

		self.draw_stage_banner()

		if self.ending_active:
			self.draw_ending_banner()
		if self.show_highscores:
			self.hud.draw_highscores(self.screen)

		if c.event == Event.PAUSE:
			pausesurface = pg.Surface((c.WIDTH, c.HEIGHT), pg.SRCALPHA)
			pausesurface.fill((0, 0, 0, 120))
			mixer.fadeout(1000)
			pausetext = self.game_over_font.render("| |", True, (255, 255, 255))
			pause_rect = pausetext.get_rect(center=(c.WIDTH // 2, c.HEIGHT // 2))
			pausesurface.blit(pausetext, pause_rect)
			self.screen.blit(pausesurface, (0, 0))

		if self.fade_alpha > 0:
			overlay = pg.Surface((c.WIDTH, c.HEIGHT), pg.SRCALPHA)
			overlay.fill((0, 0, 0, self.fade_alpha))
			self.screen.blit(overlay, (0, 0))

		pg.display.flip()

	def draw_ending_banner(self):
		if not self.ending_active:
			return
		if self.game_over and not self.victory:
			self.draw_game_over()
			return

		overlay = pg.Surface((c.WIDTH, c.HEIGHT), pg.SRCALPHA)

		if self.victory:
			overlay.fill((0, 20, 45, 120))
		else:
			overlay.fill((0, 0, 0, 150))

		self.screen.blit(overlay, (0, 0))

		banner_width = c.WIDTH
		banner_height = 500

		banner_y = c.HEIGHT // 2 - banner_height // 2

		banner = pg.Surface((banner_width, banner_height), pg.SRCALPHA)
		frame_color = (120, 255, 120)
		main_color = (220, 255, 255)
		sub_color = (180, 230, 255)

		if self.victory:
			banner.fill((20, 60, 90, 210))
			main_text = "MISSION COMPLETE"
			sub_text = "DARK VOID HAS BEEN SILENCED"
			self.killed_by = "No-one"
		else:
			main_text = "YOU DIED"
			sub_text = (
				f"YOU HAVE BEEN HUMILIATED BY {self.killed_by or self.player.killed_by}"
			)
			self.draw_game_over()

		self.screen.blit(banner, (0, banner_y))

		pg.draw.line(self.screen, frame_color, (0, banner_y), (c.WIDTH, banner_y), 10)

		pg.draw.line(
			self.screen,
			frame_color,
			(0, banner_y + banner_height),
			(c.WIDTH, banner_y + banner_height),
			10,
		)

		text = self.nerd_font.render(main_text, True, main_color)
		text_rect = text.get_rect(center=(c.WIDTH // 2, c.HEIGHT // 2 - 18))
		self.screen.blit(text, text_rect)

		sub = self.medium_nerd.render(sub_text, True, sub_color)
		sub_rect = sub.get_rect(center=(c.WIDTH // 2, c.HEIGHT // 2 + 80))
		self.screen.blit(sub, sub_rect)

	pg.display.flip()

	def update_stage_banner(self, dt):
		if self.stage_banner_timer > 0:
			self.stage_banner_timer = max(0, self.stage_banner_timer - dt)

	def draw_stage_banner(self):
		if self.stage_banner_timer <= 0:
			return

		fade = min(1, self.stage_banner_timer / 0.35)
		alpha = int(230 * fade)
		banner_height = 140
		banner = pg.Surface((c.WIDTH, banner_height), pg.SRCALPHA)
		banner.fill((95, 95, 220, alpha))

		white_rect = pg.Rect(0, 10, c.WIDTH, 120)
		pg.draw.rect(banner, (255, 255, 255, alpha), white_rect)


		label = self.stage_banner_text or f"STAGE {self.level.stage}"
		stage_text = self.stage_font.render(label, True, (0, 0, 0))

		stage_text.set_alpha(alpha)
		stage_rect = stage_text.get_rect(center=(c.WIDTH // 2, banner_height // 2))
		banner.blit(stage_text, stage_rect)

		self.screen.blit(banner, (0, c.HEIGHT // 2 - banner_height // 2))

	def draw_game_over(self):
		overlay_alpha = min(180, 80 + int(self.game_over_timer * 90))
		overlay = pg.Surface((c.WIDTH, c.HEIGHT), pg.SRCALPHA)
		overlay.fill((0, 0, 0, overlay_alpha))
		self.screen.blit(overlay, (0, 0))
		if not self.gameoversound_played:
			self.gameoversound_played = True
			mixer.set_num_channels(2)
			gameover = mixer.Sound(Path(c.HOME_DIR, "assets", "audio", "gameover.wav"))
			mixer.Sound(gameover).set_volume(0.4)
			gameover.play()
			mixer.Sound(Path(c.HOME_DIR, "assets", "audio", "gameover.wav")).play()

		banner_height = 180
		banner = pg.Surface((c.WIDTH, banner_height), pg.SRCALPHA)
		banner.fill((0, 0, 0, 220))
		self.screen.blit(banner, (0, c.HEIGHT // 2 - banner_height // 2))

		scale = min(1.0, 0.75 + self.game_over_timer * 1.8)
		text = pg.transform.smoothscale_by(self.game_over_text, scale)
		text_rect = text.get_rect(center=(c.WIDTH // 2, c.HEIGHT // 2))
		self.screen.blit(text, text_rect)
		small_text = self.small_nerd.render(
			f"You were humiliated by {self.player.killer or self.killed_by}",
			True,
			(255, 255, 255),
		)
		small_text_rect = small_text.get_rect(
			center=(c.WIDTH // 2, c.HEIGHT // 2 + 100)
		)
		self.screen.blit(small_text, small_text_rect)
	pg.display.flip()

	def mask_collide(self, sprite_a, sprite_b):
		if not hasattr(sprite_a, "mask"):
			sprite_a.mask = pg.mask.from_surface(sprite_a.image)

		if not hasattr(sprite_b, "mask"):
			sprite_b.mask = pg.mask.from_surface(sprite_b.image)

		offset = (
			sprite_b.rect.left - sprite_a.rect.left,
			sprite_b.rect.top - sprite_a.rect.top
		)

		return sprite_a.mask.overlap(sprite_b.mask, offset) is not None

	def handle_collisions(self):
		# Player bullets vs enemies and bosses
		for enemy in list(self.enemies):
			for bullet in list(self.player_bullets):
				if not enemy.rect.colliderect(bullet.rect):
					continue

				if not self.mask_collide(enemy, bullet):
					continue

				damage = getattr(bullet, "damage", 1)

				if not getattr(bullet, "piercing", False):
					bullet.kill()

				if hasattr(enemy, "damage"):
					enemy.damage(damage)
				else:
					enemy.kill()

				break

		# Player bullets vs asteroids
		for asteroid in list(self.asteroids):
			for bullet in list(self.player_bullets):
				if not asteroid.rect.colliderect(bullet.rect):
					continue

				if not self.mask_collide(asteroid, bullet):
					continue

				damage = getattr(bullet, "damage", 1)

				if not getattr(bullet, "piercing", False):
					bullet.kill()

				if hasattr(asteroid, "damage"):
					asteroid.damage(damage)
				else:
					asteroid.kill()

				break

		# Enemy bullets vs player
		if self.player.alive and self.player.invincible_timer <= 0:
			for bullet in list(self.enemy_bullets):
				bullet_pos = getattr(bullet, "pos", pg.Vector2(bullet.rect.center))
				bullet_radius = getattr(
					bullet, "radius", max(bullet.rect.width, bullet.rect.height) // 2
				)

				distance = self.player.pos.distance_to(bullet_pos)

				if distance < self.player.hitbox_radius + bullet_radius:
					bullet.kill()

					lives_before = self.player.lives
					self.player.receive_hit()

					if lives_before > 0 and self.player.lives <= 0:
						killer_name = getattr(bullet, "owner", "the Illithids")
						self.killed_by = killer_name
						self.player.alive = False
						self.end_game(victory=False)
					break

		# Asteroids vs player
		if self.player.alive and self.player.invincible_timer <= 0:
			for asteroid in list(self.asteroids):
				asteroid_hitbox = getattr(asteroid, "hitbox", asteroid.rect)

				if asteroid_hitbox.colliderect(self.player.rect):
					lives_before = self.player.lives
					self.player.receive_hit()

					if lives_before > 0 and self.player.lives <= 0:
						enemy_name = getattr(asteroid, "name", "a Rock")
						self.killed_by = enemy_name
						self.player.alive = False
						self.game_over = True

					break

		# Enemy / boss body vs player
		if self.player.alive and self.player.invincible_timer <= 0:
			for enemy in list(self.enemies):
				enemy_hitbox = getattr(enemy, "hitbox", enemy.rect)

				if enemy_hitbox.colliderect(self.player.rect):
					lives_before = self.player.lives
					self.player.receive_hit()

					if lives_before > 0 and self.player.lives <= 0:
						enemy_name = getattr(enemy, "name", "the Illithids")
						self.killed_by = enemy_name
						self.player.alive = False
						self.game_over = True

					break

		# Powerups vs player
		powerup_hits = pg.sprite.spritecollide(self.player, self.powerups, True)

		for powerup in powerup_hits:
			self.player.apply_powerup(powerup.kind)

	def end_game(self, victory=False):
		if self.ending_active:
			return

		self.victory = victory
		self.game_over = True
		self.ending_active = True
		self.ending_timer = 0

		self.show_highscores = False
		self.entering_highscore = False
		self.highscore_sequence_started = False

	def start_highscore_entry(self):
		if self.score_saved or self.entering_highscore:
			return

		if self.highscores.is_high_score(self.score):
			self.entering_highscore = True
			self.highscore_name = ""
			pg.key.start_text_input()
		else:
			self.score_saved = True

	def submit_highscore(self):
		if self.highscore_saved:
			return

		name = self.highscore_name.strip()

		if not name:
			name = "???"

		self.highscores.add_score(
			name=name,
			score=self.score,
			level=self.level.stage,
			killed_by=self.killed_by or self.player.killed_by or "the Illithids",
		)

		self.highscore_saved = True
		self.entering_highscore = False
		self.score_saved = True
		self.show_highscores = True
		pg.key.stop_text_input()

	def run(self):
		while self.running:
			dt = self.clock.tick(c.FPS) / 1000

			for event in pg.event.get():
				if event.type == pg.QUIT:
					self.running = False
				if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
					self.highscore_name = "shS"
					self.submit_highscore()
					self.running = False
				if self.show_highscores and not self.entering_highscore:
					if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
						self.restart_requested = True
						self.running = False
						break

				if event.type == pg.KEYDOWN and event.key == pg.K_PAUSE:
					if c.event == Event.PAUSE:
						mixer.music.play(-1)
						c.event = Event.PLAYING
					elif c.event != Event.PAUSE:
						c.event = Event.PAUSE
				if event.type == pg.KEYDOWN and event.key == pg.K_LALT:
					self.player.activate_shield()
				if self.entering_highscore:
					if event.type == pg.TEXTINPUT:
						if len(self.highscore_name) < self.max_name_length:
							if event.text.isprintable():
								self.highscore_name += event.text

					elif event.type == pg.KEYDOWN:
						if event.key == pg.K_BACKSPACE:
							self.highscore_name = self.highscore_name[:-1]
						elif event.key == pg.K_RETURN:
							self.submit_highscore()
					if event.type == pg.KEYDOWN:
						if event.key == pg.K_LSHIFT:
							self.player.speed = self.player.focus_speed
						if (
							event.type == pg.KEYDOWN
							and event.key == pg.K_LALT
							and self.player.shield_amount > 0
							and not self.player.shield_active
						):
							self.player.shield_active = True
							self.player.shield_amount -= 1

							shield = Shield(self, self.player)

							self.effects.add(shield)
							self.all_sprites.add(shield)
						if event.type == pg.KEYUP:
							self.player.speed = c.PLAYER_SPEED

						if c.DEBUG:
							if event.type == pg.KEYDOWN and event.key == pg.K_F11:
								self.player.alive = False

			if c.event != Event.PAUSE:
				self.update(dt)
			self.draw()

		return "restart" if self.restart_requested else "quit"


if __name__ == "__main__":
	game = Game()
	game.run()
