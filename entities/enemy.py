import pygame as pg
import config as c
from pygame.transform import rotozoom
from magic.pox_module import add_charge
from magic.anim_module import new_explosion


class Enemy(pg.sprite.Sprite):
	def __init__(self, game, pos):
		super().__init__()

		self.game = game

		self.image = rotozoom(pg.image.load("assets/alus2.png").convert_alpha(), 180, 0.3)

		self.rect = self.image.get_rect(center=pos)
		self.pos = pg.Vector2(self.rect.center)

		self.hp = 5
		self.speed = 80

	def update(self, dt):
		self.pos.y += self.speed * dt
		self.rect.center = self.pos

		if self.rect.top > c.HEIGHT:
			self.kill()

	def damage(self, amount):
		self.hp -= amount

		if self.hp <= 0:
			self.kill()
