class BulletManager:
	def __init__(self, game):
		self.game = game

	def clear_enemy_bullets(self):
		for bullet in self.game.enemy_bullets:
			bullet.kill()
