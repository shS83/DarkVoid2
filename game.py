import random
from errno import EOWNERDEAD

from systems.highscores import HighScoreTable
from icecream import ic
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
import config as c


def mixing():
	mixer.init()
	tunes = ["1000 Handz - Reps.mp3", "1000 Handz - Announcement.mp3", "1000 Handz - No Option.mp3",
	         "Colorcast - Coffee Break.mp3", "Colorcast - Drown.mp3", "Colorcast - Need.mp3",
	         "Jahzzar - Forest Pan.mp3", "Jahzzar - Pink Fluid.mp3", "Lightning Traveler - Celestial Drift.mp3",
	         "Lightning Traveler - Eclipse Horizon.mp3", "Lightning Traveler - Event Horizon.mp3",
	         "Lightning Traveler - Lunar Echo.mp3", "Ov Moi Omm - The Dictator’s Transmission (YSMHB).mp3"]
	mixer.music.load(c.resource_path(Path(c.HOME_DIR, "assets", "audio", random.choice(tunes))))
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
		self.bosses=[]
		self.highscores = HighScoreTable(
			Path(c.HOME_DIR, "highscores.json")
		)
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
		self.rock_images = []
		for i in range(1, 5):
			img = pg.image.load(c.resource_path(Path(c.HOME_DIR, "assets", "rocks", f"rock_{i}.png"))).convert_alpha()
			self.rock_images.append(img)
		for i in range(1, 32):
			img = pg.image.load(c.resource_path(Path(c.HOME_DIR, "assets", "explosions", f"exp_{i}.png"))).convert_alpha()
			img = pg.transform.scale(img, (320, 320))
			self.explosion_frames.append(img)
		for i in range(1, 32):
			img = pg.image.load(c.resource_path(Path(c.HOME_DIR, "assets", "explosions", f"exp_{i}.png"))).convert_alpha()
			img = pg.transform.scale(img, (640, 640))
			self.boss_explosion_frames.append(img)
		self.background = pg.image.load(c.resource_path(Path(c.HOME_DIR, "assets", "backgrounds", "space_background.png"))).convert()
		self.background = pg.transform.scale(self.background, (c.WIDTH, c.HEIGHT))
		self.direction = 1
		self.px = c.WIDTH // 2
		self.py = -42
		self.dt = 0
		self.all_sprites = pg.sprite.LayeredUpdates()
		self.game_over_font = pg.font.Font(Path(c.HOME_DIR, "assets", "fonts", "JetBrainsMonoNerdFont-SemiBold.ttf"), 96)
		self.stage_font = pg.font.Font(Path(c.HOME_DIR, "assets", "fonts", "JetBrainsMonoNerdFont-SemiBold.ttf"), 96)
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
		self.nerd_font = pg.font.Font(Path(c.HOME_DIR, "assets", "fonts", "MonaspiceXeNerdFontPropo-Light.otf"), 128)
		self.medium_nerd = pg.font.Font(Path(c.HOME_DIR, "assets", "fonts", "MonaspiceXeNerdFontPropo-Light.otf"), 56)
		self.small_nerd = pg.font.Font(Path(c.HOME_DIR, "assets", "fonts", "MonaspiceXeNerdFontPropo-Light.otf"), 28)
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

		for _ in range(200):
			self.stars.add(Star())

	@staticmethod
	def play_sound(sound, volume=1.0):
		channel = pg.mixer.find_channel(True)

		if channel:
			sound.set_volume(volume)
			channel.play(sound)

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
			self.game_over = True

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
					self.damage_player(killer="The Rock")
					break

			if not overlap:
				asteroid = Meteor(self, (x, y))
				self.asteroids.add(asteroid)
				self.all_sprites.add(asteroid)
				return


	def spawn_enemy(self):
		c.NEXTBOSS: dict | None = None
		if random.random() < 0.15:
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
				if self.player.rect.colliderect(enemy.rect) and not self.player.invincible_timer > 0:
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


		if self.player.rect.colliderect(self.boss.rect) and not self.player.invincible_timer > 0:
			self.damage_player(killer=self.boss.name)
		return self.boss

	def update(self, dt):
		self.stars.update(dt)
		self.all_sprites.update(dt)

		if self.level.stage != self.stage_banner_stage:
			self.stage_banner_stage = self.level.stage
			self.stage_banner_timer = self.stage_banner_duration
			c.event = Event.PLAYING

		if self.stage_banner_timer > 0:
			self.stage_banner_timer = max(0, self.stage_banner_timer - dt)

		if self.game_over:
			self.game_over_timer += dt

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

				if len(self.asteroids) < self.level.max_asteroids:
					self.spawn_asteroid()

			if (
					self.level_timer >= self.boss_spawn_delay
					and self.boss is None
			):
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
		self.screen.blit(self.background, (0, 0))
		self.stars.draw(self.screen)
		self.all_sprites.draw(self.screen)
		self.hud.draw(self.screen)

		if c.DEBUG:
			if self.boss is not None:
				pg.draw.rect(self.screen, (255, 0, 0), self.boss.hitbox, 3)
			pg.draw.rect(self.screen, (255, 0, 0), self.player.hitbox, 3)


		self.draw_stage_banner()
		self.draw_game_over()

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

		pg.display.flip()

	def draw_stage_banner(self):
		gameover_played = False
		if self.stage_banner_timer <= 0:
			return
		if self.level.stage == 5:
			fade = min(1, self.final_banner_timer / 0.35)
			alpha = int(230 * fade)
			banner_height = 300
			banner = pg.Surface((c.WIDTH, banner_height), pg.SRCALPHA)
			banner.fill((0, 255, 0, alpha))
			if not self.gameoversound_played:
				mixer.set_num_channels(2)
				gameover = mixer.Sound(Path(c.HOME_DIR, "assets", "audio", "gameover.wav"))
				mixer.Sound(gameover).set_volume(0.4)
				gameover.play()
				mixer.Sound(Path(c.HOME_DIR, "assets", "audio", "gameover.wav")).play()
				self.gameoversound_played = True
			white_rect = pg.Rect(0, 30, c.WIDTH, 240)
			pg.draw.rect(banner, (255, 255, 255, alpha), white_rect)
			stage_text = self.stage_font.render(f"YOU CONQUERED SPACE", True, (0, 0, 0))
			stage_text.set_alpha(alpha)
			stage_rect = stage_text.get_rect(center=(c.WIDTH // 2, banner_height // 2))
			banner.blit(stage_text, stage_rect)
			self.screen.blit(banner, (0, c.HEIGHT // 2 - banner_height // 2))
			self.player.visible = False
			self.all_sprites.remove(self.player)
			self.end_game(victory=True)
			if not self.player.visible and not self.score_saved:
				self.start_highscore_entry()
			if not self.player.visible:
				self.hud.draw_highscores(self.screen)
		else:
			fade = min(1, self.stage_banner_timer / 0.35)
			alpha = int(230 * fade)
			banner_height = 140
			banner = pg.Surface((c.WIDTH, banner_height), pg.SRCALPHA)
			banner.fill((95, 95, 220, alpha))

			white_rect = pg.Rect(0, 10, c.WIDTH, 120)
			pg.draw.rect(banner, (255, 255, 255, alpha), white_rect)

			stage_text = self.stage_font.render(f"STAGE {self.level.stage}", True, (0, 0, 0))
			stage_text.set_alpha(alpha)
			stage_rect = stage_text.get_rect(center=(c.WIDTH // 2, banner_height // 2))
			banner.blit(stage_text, stage_rect)

			self.screen.blit(banner, (0, c.HEIGHT // 2 - banner_height // 2))

	def draw_game_over(self):

		if not self.game_over:
			return

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

		if self.game_over and not self.score_saved:
			self.start_highscore_entry()

		banner_height = 180
		banner = pg.Surface((c.WIDTH, banner_height), pg.SRCALPHA)
		banner.fill((0, 0, 0, 220))
		self.screen.blit(banner, (0, c.HEIGHT // 2 - banner_height // 2))

		scale = min(1.0, 0.75 + self.game_over_timer * 1.8)
		text = pg.transform.smoothscale_by(self.game_over_text, scale)
		text_rect = text.get_rect(center=(c.WIDTH // 2, c.HEIGHT // 2))
		self.screen.blit(text, text_rect)
		small_text = self.small_nerd.render(f"You were humiliated by {self.player.killer or game.killed_by}", True, (255, 255, 255))
		small_text_rect = small_text.get_rect(center=(c.WIDTH // 2, c.HEIGHT // 2 + 100))
		self.screen.blit(small_text, small_text_rect)

	def handle_collisions(self):
		# Player bullets vs asteroids
		for asteroid in list(self.asteroids):
			asteroid_hitbox = getattr(asteroid, "hitbox", asteroid.rect)

			for bullet in list(self.player_bullets):
				if asteroid_hitbox.colliderect(bullet.rect):
					bullet.kill()

					if hasattr(asteroid, "damage"):
						asteroid.damage(1)
					else:
						asteroid.kill()
					break

		# Player bullets vs enemies and bosses
		for enemy in list(self.enemies):
			enemy_hitbox = getattr(enemy, "hitbox", enemy.rect)

			for bullet in list(self.player_bullets):
				if enemy_hitbox.colliderect(bullet.rect):
					damage = getattr(bullet, "damage", 1)

					if not getattr(bullet, "piercing", False):
						bullet.kill()

					if hasattr(enemy, "damage"):
						enemy.damage(damage)
					else:
						enemy.kill()

					break

		# Enemy bullets vs player
		if self.player.alive and self.player.invincible_timer <= 0:
			for bullet in list(self.enemy_bullets):
				bullet_pos = getattr(bullet, "pos", pg.Vector2(bullet.rect.center))
				bullet_radius = getattr(
					bullet,
					"radius",
					max(bullet.rect.width, bullet.rect.height) // 2
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
		powerup_hits = pg.sprite.spritecollide(
			self.player,
			self.powerups,
			True
		)

		for powerup in powerup_hits:
			self.player.apply_powerup(powerup.kind)

	def end_game(self, victory=False):
		if self.game_over and self.show_highscores:
			return

		self.victory = victory
		self.game_over = True
		self.show_highscores = True

		self.start_highscore_entry()

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
			killed_by=self.killed_by or "the Illithids"
		)

		self.highscore_saved = True
		self.entering_highscore = False
		self.score_saved = True
		pg.key.stop_text_input()

	def run(self):
		while self.running:
			dt = self.clock.tick(c.FPS) / 1000

			for event in pg.event.get():
				if event.type == pg.QUIT:
					self.running = False
				if event.type == pg.KEYDOWN and event.key == pg.K_F11:
					self.player.alive = False
				if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
					self.highscore_name = "shS"
					self.submit_highscore()
					self.running = False
				if event.type == pg.KEYDOWN and event.key == pg.K_PAUSE:
					if c.event == Event.PAUSE:
						mixer.music.play(-1)
						c.event = Event.PLAYING
					elif c.event != Event.PAUSE:
						c.event = Event.PAUSE
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

						if c.DEBUG:
							if self.player.visible:
								if event.type == pg.KEYDOWN and event.key == pg.K_F2:
									self.boss_spawn(c.BOSS.pop(0))
						if event.type == pg.KEYDOWN:
							if event.key == pg.K_LSHIFT:
								self.player.speed = self.player.focus_speed
							if (
									event.type == pg.KEYDOWN
									and event.key == pg.K_LALT
									and self.player.shield_amount > 0
									and not self.player.shield_active
							):
								print("Shield activated. Charges left:", self.player.shield_amount)
								self.player.shield_active = True
								self.player.shield_amount -= 1

								shield = Shield(self, self.player)

								self.effects.add(shield)
								self.all_sprites.add(shield)

					if event.type == pg.KEYUP and event.key == pg.K_LSHIFT:
						self.player.speed = c.PLAYER_SPEED

			if c.event != Event.PAUSE:
				self.update(dt)
			self.draw()

	pg.quit()
	mixer.quit()

if __name__ == "__main__":
	game = Game()
	game.run()
