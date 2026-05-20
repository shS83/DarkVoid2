import pygame as pg
import config as c
from pygame.transform import rotozoom
from magic.pox_module import add_charge
from magic.anim_module import new_explosion
from entities.explosion import Explosion


class Enemy(pg.sprite.Sprite):
	def __init__(self, game, pos):
		super().__init__()

		self.game = game

		self.image = rotozoom(pg.image.load("assets/alus2.png").convert_alpha(), 180, 0.3)
		self.base_image = self.image.copy()
		self.flash_image = self.make_flash_image(self.base_image)
		self.flash_timer = 0
		self.rect = self.image.get_rect(center=pos)
		self.pos = pg.Vector2(self.rect.center)

		self.hp = 5
		self.speed = 80

	def make_flash_image(self, image):
		flash = image.copy()
		flash.fill((255, 255, 255, 180), special_flags=pg.BLEND_RGBA_ADD)
		return flash

	def update(self, dt):
		self.pos.y += self.speed * dt
		self.rect.center = self.pos
		if self.flash_timer > 0:
			self.flash_timer -= dt
			self.image = self.flash_image
		else:
			self.image = self.base_image
		if self.rect.top > c.HEIGHT:
			self.kill()

	def damage(self, amount):
		self.hp -= amount
		self.flash_timer = 0.1

		if self.hp <= 0:
			self.destroy()

	def destroy(self):
		explosion = Explosion(self.game, self.rect.center)
		self.game.effects.add(explosion)
		self.game.all_sprites.add(explosion)

		self.kill()
