import pygame as pg
import pygame.gfxdraw
import config as c
from entities.player import Player
from entities.enemy import Enemy
from entities.star import Star
import random
from ui.hud import HUD


class Game:
	def __init__(self):
		pg.init()
		pg.mixer.init()
		pg.mixer.set_num_channels(32)
		self.score = 0
		self.hud = HUD(self)
		self.screen = pg.display.set_mode((c.WIDTH, c.HEIGHT))
		self.clock = pg.time.Clock()
		self.running = True
		self.effects = pg.sprite.Group()
		self.explosion_frames = []
		self.enemy_spawn_timer = 0
		self.enemy_spawn_delay = random.uniform(1.5, 5.0)
		for i in range(1, 32):
			img = pg.image.load(f"{c.HOME_DIR}/assets/exp_{i}.png").convert_alpha()
			img = pg.transform.scale(img, (320, 320))
			self.explosion_frames.append(img)
		self.background = pg.image.load(f"{c.HOME_DIR}/assets/space_background.jpg").convert()
		self.background = pg.transform.scale(self.background, (c.WIDTH, c.HEIGHT))
		self.enemies = pg.sprite.Group()
		self.enemy_bullets = pg.sprite.Group()
		self.texts = pg.sprite.Group()
		self.all_sprites = pg.sprite.Group()
		self.game_over = False
		self.game_over_angle = 0
		self.game_over_scale = 0.5
		self.game_over_scale_dir = 1
		self.game_over_font = c.MSG_FONT
		self.game_over_backdrop_scale = 0.1
		self.game_over_backdrop_alpha = 220
		self.text_alpha = 255
		self.game_over_text = self.game_over_font.render("GAME OVER", True, (255, 40, 40))
		self.player = Player(self, (c.WIDTH // 2, c.HEIGHT - 90))
		self.all_sprites.add(self.player)
		self.player_bullets = pg.sprite.Group()
		enemy = Enemy(self, (c.WIDTH // 2, -80))
		self.enemies.add(enemy)
		self.all_sprites.add(enemy)
		self.stars = pg.sprite.Group()

		for _ in range(200):
			self.stars.add(Star())

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

	def update(self, dt):
		self.stars.update(dt)
		self.all_sprites.update(dt)
		self.enemy_spawn_timer += dt

		if self.enemy_spawn_timer >= self.enemy_spawn_delay:
			self.enemy_spawn_timer = 0
			self.enemy_spawn_delay = random.uniform(0.4, 3)
			self.spawn_enemy()

		hits = pg.sprite.groupcollide(
			self.enemies,
			self.player_bullets,
			False,
			True
		)

		if self.player.alive and self.player.invincible_timer <= 0:
			for bullet in self.enemy_bullets:
				distance = self.player.pos.distance_to(bullet.pos)

				if distance < self.player.hitbox_radius + bullet.radius:
					bullet.kill()
					self.player.hit()
					break

		if not self.player.alive:
			self.game_over = True

		for enemy, bullets in hits.items():
			enemy.damage(len(bullets))

		if self.game_over:
			self.game_over_scale += self.game_over_scale_dir * 0.2 * dt
			self.text_alpha -= 0.5
			self.game_over_backdrop_scale += 2.8 * dt
			if self.game_over_backdrop_scale > 6:
				self.game_over_backdrop_scale = 6
			self.game_over_backdrop_alpha -= 50 * dt
			if self.game_over_backdrop_alpha < 80:
				self.game_over_backdrop_alpha = 80
			return

	def draw(self):
		self.screen.blit(self.background, (0, 0))
		self.all_sprites.draw(self.screen)
		self.stars.draw(self.screen)
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
			self.update(dt)
			self.draw()

		pg.quit()
