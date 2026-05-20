import pygame as pg
import config as c
from entities.player import Player
from entities.enemy import Enemy

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
		for i in range(1, 32):
			img = pg.image.load(f"assets/exp_{i}.png").convert_alpha()
			img = pg.transform.scale(img, (160, 160))
			self.explosion_frames.append(img)
		self.background = pg.image.load("assets/space_background_2.jpg").convert()
		self.background = pg.transform.scale(self.background, (c.WIDTH, c.HEIGHT))
		self.enemies = pg.sprite.Group()
		self.all_sprites = pg.sprite.Group()
		self.player = Player(self, (c.WIDTH // 2, c.HEIGHT - 90))
		self.all_sprites.add(self.player)
		self.player_bullets = pg.sprite.Group()
		enemy = Enemy(self, (c.WIDTH // 2, 80))
		self.enemies.add(enemy)
		self.all_sprites.add(enemy)

	def run(self):
		while self.running:
			dt = self.clock.tick(c.FPS) / 1000

			for event in pg.event.get():
				if event.type == pg.QUIT:
					self.running = False

			self.all_sprites.update(dt)
			self.all_sprites.update(dt)

			hits = pg.sprite.groupcollide(
				self.enemies,
				self.player_bullets,
				False,
				True
			)

			for enemy, bullets in hits.items():
				enemy.damage(len(bullets))
			self.screen.blit(self.background, (0, 0))
			self.all_sprites.draw(self.screen)

			pg.display.flip()

		pg.quit()
