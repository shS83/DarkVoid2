import pygame as pg
import config as c
from entities.player import Player
from entities.enemy import Enemy
from entities.star import Star
import random
from core.gameover_text import Gameover


class Game:
	def __init__(self):
		pg.init()
		self.screen = pg.display.set_mode((c.WIDTH, c.HEIGHT))
		self.clock = pg.time.Clock()
		self.running = True
		self.effects = pg.sprite.Group()
		self.explosion_frames = []
		self.enemy_spawn_timer = 0
		self.enemy_spawn_delay = random.uniform(0.5, 2.0)
		for i in range(1, 32):
			img = pg.image.load(f"assets/exp_{i}.png").convert_alpha()
			img = pg.transform.scale(img, (320, 320))
			self.explosion_frames.append(img)
		self.background = pg.image.load("assets/space_background_2.jpg").convert()
		self.background = pg.transform.scale(self.background, (c.WIDTH, c.HEIGHT))
		self.enemies = pg.sprite.Group()
		self.enemy_bullets = pg.sprite.Group()
		self.texts = pg.sprite.Group()
		self.all_sprites = pg.sprite.Group()
		self.gameover = False
		self.gameovertext = Gameover()
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

		if self.gameover:
			self.gameovertext.update(dt)

		for enemy, bullets in hits.items():
			enemy.damage(len(bullets))

	def draw(self):
		self.screen.blit(self.background, (0, 0))
		self.all_sprites.draw(self.screen)
		self.stars.draw(self.screen)
		self.texts.draw(self.screen)
		if self.gameover:
			self.gameovertext.draw(self.screen)
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
