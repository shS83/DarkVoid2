import config as c
from entities.enemy import Enemy


class StageManager:
	def __init__(self, game):
		self.game = game
		self.time = 0
		self.events = [
			(1.0, self.wave_one),
			(4.0, self.wave_two),
			(8.0, self.wave_three),
		]
		self.index = 0

	def update(self, dt):
		self.time += dt

		while self.index < len(self.events) and self.time >= self.events[self.index][0]:
			_, callback = self.events[self.index]
			callback()
			self.index += 1

	def spawn_enemy(self, x, y=-40, hp=20):
		enemy = Enemy(self.game, (x, y), hp=hp)
		self.game.enemies.add(enemy)
		self.game.all_sprites.add(enemy)

	def wave_one(self):
		for x in [120, 220, 320, 420, 520]:
			self.spawn_enemy(x)

	def wave_two(self):
		for x in [80, 200, 440, 560]:
			self.spawn_enemy(x, hp=35)

	def wave_three(self):
		for x in [160, 320, 480]:
			self.spawn_enemy(x, hp=50)
