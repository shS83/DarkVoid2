class Level:
	def __init__(self):
		self.stage = 1
		self.asteroids = 7
		self.asteroid_speed = 1
		self.asteroid_hp = 1

	def up(self):
		self.stage += 1
		self.asteroids += 1
		self.asteroid_speed += 0.20
		self.asteroid_hp += 0.20


level = Level()
