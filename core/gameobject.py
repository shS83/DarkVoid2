import pygame as pg
from pygame import Vector2
from core.utils import wrap_position
from pygame.locals import *


class GameObject(pg.sprite.Sprite):
	def __init__(self, position, image, velocity=Vector2(0, 0)):
		super().__init__()

		self.original_image = image.convert_alpha()
		self.image = self.original_image
		self.rect = self.image.get_rect(center=position)

		self.position = Vector2(position)
		self.velocity = Vector2(velocity)
		self.rotation = 0
		self.scale = 1.0

	def update(self, dt):
		self.position += self.velocity * dt
		self.rect.center = self.position

	def draw(self, surface):
		blit_position = self.position - Vector2(self.radius)
		surface.blit(self.sprite, blit_position)

	def move(self, surface):
		self.position = wrap_position(self.position + self.velocity, surface)

	def collides_with(self, other_obj):
		distance = self.position.distance_to(other_obj.position)
		return distance < self.radius + other_obj.radius

	def collides_with_tolerance(self, other_obj, tolerance):
		distance = self.position.distance_to(other_obj.position)
		return distance < self.radius + other_obj.radius + tolerance

	def collides_with_any(self, other_obj_list):
		colliders = False
		for obj in other_obj_list:
			if not hasattr(obj, 'position'):
				continue
			distance = self.position.distance_to(obj.position)
			if distance < self.radius + obj.radius:
				colliders = True
		return colliders
