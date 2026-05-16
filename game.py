import pygame as pg
import config as c

from entities.player import Player
from systems.stage_manager import StageManager
from systems.collision import CollisionSystem
from systems.bullet_manager import BulletManager
from systems.scoring import ScoreSystem
from ui.hud import HUD


class Game:
	def __init__(self):
		pg.init()
		self.screen = pg.display.set_mode((c.WIDTH, c.HEIGHT))
		self.clock = pg.time.Clock()
		self.running = True
		self.dt = 0

		self.all_sprites = pg.sprite.Group()
		self.enemies = pg.sprite.Group()
		self.player_bullets = pg.sprite.Group()
		self.enemy_bullets = pg.sprite.Group()
		self.effects = pg.sprite.Group()
		self.items = pg.sprite.Group()

		self.score = ScoreSystem()
		self.bullets = BulletManager(self)
		self.collision = CollisionSystem(self)
		self.stage = StageManager(self)
		self.hud = HUD(self)

		self.player = Player(self, (c.WIDTH // 2, c.HEIGHT - 80))
		self.all_sprites.add(self.player)

	def run(self):
		while self.running:
			self.dt = self.clock.tick(c.FPS) / 1000
			self.handle_events()
			self.update()
			self.draw()

		pg.quit()

	def handle_events(self):
		for event in pg.event.get():
			if event.type == pg.QUIT:
				self.running = False
			elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
				self.running = False

	def update(self):
		self.stage.update(self.dt)
		self.all_sprites.update(self.dt)
		self.collision.update()

	def draw(self):
		self.screen.fill((8, 8, 16))
		self.all_sprites.draw(self.screen)
		self.hud.draw(self.screen)
		pg.display.flip()
