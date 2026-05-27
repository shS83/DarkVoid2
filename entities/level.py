import random
import config as c
from pathlib import Path
import pygame as pg

class Level:
	def __init__(self):
		self.stage = 1
		self.asteroids = 3
		self.lives = 3
		self.enemy_spawn_delay = random.uniform(2, 6.0)
		self.enemy_spawn_timer = 0
		self.asteroid_spawn_timer = 0
		self.asteroid_spawn_delay = 15
		self.enemy_bullet_cooldown = 0.3
		self.max_enemies = 4
		self.player_shield_amount = 5
		self.enemy_hp = 5
		self.asteroid_hp = 2
		self.boss = None
		self.next_boss_candidate = None
		self.boss_timer = 2000
		self.boss_hp = 300
		self.max_asteroids = 6
		self.asteroid_speed = 1


	def up(self):
		#self.next_boss_candidate = self.boss_tree.pop(0)
		self.player_shield_amount += 1
		self.enemy_bullet_cooldown -= 0.03
		self.stage += 1
		self.lives += 2
		self.max_enemies += 1
		self.asteroids += 1
		self.asteroid_hp += 1
		self.enemy_hp += 1
		self.enemy_bullet_cooldown -= 0.05
		self.max_asteroids += 1
		self.max_enemies += 2
		self.asteroid_speed += 0.20
		self.asteroid_hp += 0.20
		self.boss_timer += 1000
		self.boss_hp += 100

level = Level()
