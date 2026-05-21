import pygame as pg
import config as c
from core.commons import *
from core.utils import get_random_velocity, get_random_position
from entities.bullet import PlayerBullet
from entities.explosion import Explosion
from entities.particle import Particle
import random
from pygame.transform import rotozoom
from core.spritegroups import all_sprites, asteroid_group, Asteroid
from pygame.math import Vector2


class Meteor(pg.sprite.Sprite):
	def __init__(self, game, image: pg.Surface, pos: Vector2, vel: Vector2):
		super().__init__()
		self.image = random.choice(ROCK_IMAGES)
		self.rect = screen.get_rect(center=pos)
		self.vel = get_random_velocity(2, 10)
		self.radius = self.rect.h / 2
		self.rot = 5
		self.rot_vel = 0
		self.rot_speed = 0.005
		self.rot_max = 10
		self.rot_min = -10

	def update(self, dt):
		self.rect.x += self.vel.x * dt
		self.rect.y += self.vel.y * dt
		self.rot += self.rot_vel * dt

	def draw(self, surface):
		surface.blit(rotozoom(self.image, self.rot, 1), self.rect)

	def spawn_meteor(self, pos=get_random_position(c.screen), vel=get_random_velocity(2, 10)):
		asteroid_group.add(
			Asteroid(random.choice(ROCK_IMAGES), pos, vel))
		all_sprites.add(asteroid_group)
