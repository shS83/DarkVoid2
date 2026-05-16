import pygame as pg
import random


class Asteroid(pg.sprite.Sprite):
	def __init__(self, position, image, size):
		super().__init__()
		self.image = image
		self.rect = self.image.get_rect(center=position)


class Laser(pg.sprite.Sprite):
	def __init__(self, position, image):
		super().__init__()
		self.image = image
		self.rect = self.image.get_rect(center=position)


class Bullet(pg.sprite.Sprite):
	def __init__(self, position, image):
		super().__init__()
		self.image = image
		self.rect = self.image.get_rect(center=position)


class Enemies(pg.sprite.Sprite):
	def __init__(self, position, image):
		super().__init__()
		self.image = image
		self.rect = self.image.get_rect(center=position)


class Particles(pg.sprite.Sprite):
	def __init__(self, position, image):
		super().__init__()
		self.image = image
		self.rect = self.image.get_rect(center=position)


class Terrain(pg.sprite.Sprite):
	def __init__(self, position, image):
		super().__init__()
		self.image = image
		self.rect = self.image.get_rect(center=position)


class Powerup(pg.sprite.Sprite):
	def __init__(self, position, image):
		super().__init__()
		self.image = image
		self.rect = self.image.get_rect(center=position)


class Stars(pg.sprite.Sprite):
	def __init__(self, position, image):
		super().__init__()
		self.image = image
		self.rect = self.image.get_rect(center=position)


class Player(pg.sprite.Sprite):
	def __init__(self, position, image):
		super().__init__()
		self.image = image
		tight_rect = self.image.get_rect(center=position)
		tight_rect.inflate_ip(-10, -10)
		self.tight_rect = tight_rect


powerups_group = pg.sprite.Group()
asteroid_group = pg.sprite.Group()
particles_group = pg.sprite.Group()
enemies_group = pg.sprite.Group()
laser_group = pg.sprite.Group()
bullet_group = pg.sprite.Group()
terrain_group = pg.sprite.Group()
players = pg.sprite.Group()
star_group = pg.sprite.Group()
all_sprites = pg.sprite.LayeredUpdates()
