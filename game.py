import pygame as pg
import config as c
from entities.player import Player
from entities.enemy import Enemy
from entities.star import Star
import random
from magic.anim_module import new_explosion
from magic.pox_module import add_charge


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
		self.all_sprites = pg.sprite.Group()
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
		x = random.randint(40, c.WIDTH - 40)
		y = -80
		enemy = Enemy(self, (x, y))
		self.enemies.add(enemy)
		self.all_sprites.add(enemy)

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

		for enemy, bullets in hits.items():
			enemy.damage(len(bullets))

	def draw(self):
		self.screen.blit(self.background, (0, 0))
		self.all_sprites.draw(self.screen)
		self.stars.draw(self.screen)
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
