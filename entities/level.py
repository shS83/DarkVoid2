import random


class Level:
	def __init__(self):
		self.stage = 1
		self.asteroids = 7
		self.enemy_spawn_delay = random.uniform(1.5, 5.0)
		self.enemy_spawn_timer = 0
		self.asteroid_spawn_timer = 0
		self.asteroid_spawn_delay = 15
		self.max_asteroids = 3
		self.asteroid_speed = 1
		self.asteroid_hp = 1

	def up(self):
		self.stage += 1
		self.asteroids += 1
		self.max_asteroids += 1
		self.asteroid_speed += 0.20
		self.asteroid_hp += 0.20


level = Level()
