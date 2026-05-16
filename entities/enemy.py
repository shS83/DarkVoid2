import pygame as pg
import config as c
from systems import patterns


class Enemy(pg.sprite.Sprite):
	def __init__(self, game, pos, hp=20):
		super().__init__()
		self.game = game
		self.image = pg.Surface((46, 46), pg.SRCALPHA)
		pg.draw.polygon(self.image, (230, 80, 100), [(23, 46), (46, 0), (23, 12), (0, 0)])
		self.rect = self.image.get_rect(center=pos)
		self.pos = pg.Vector2(pos)
		self.hp = hp
		self.shoot_timer = 1.0
		self.move_speed = 80

	def update(self, dt):
		self.pos.y += self.move_speed * dt
		self.rect.center = self.pos

		self.shoot_timer -= dt
		if self.shoot_timer <= 0:
			self.shoot_timer = 1.2
			patterns.radial(self.game, self.pos, amount=16, speed=150)

		if self.rect.top > c.HEIGHT + 60:
			self.kill()

	def damage(self, amount):
		self.hp -= amount
		if self.hp <= 0:
			self.destroy()

	def destroy(self):
		self.game.score.add(100)
		self.kill()
