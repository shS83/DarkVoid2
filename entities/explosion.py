import pygame as pg


class Explosion(pg.sprite.Sprite):
	def __init__(self, game, pos):
		super().__init__()

		self.game = game
		self.frames = self.game.explosion_frames
		self.index = 0
		self.timer = 0
		self.frame_time = 0.045

		self.image = self.frames[self.index]
		self.rect = self.image.get_rect(center=pos)

	def update(self, dt):
		self.timer += dt

		if self.timer >= self.frame_time:
			self.timer = 0
			self.index += 1

			if self.index >= len(self.frames):
				self.kill()
				return

			center = self.rect.center
			self.image = self.frames[self.index]
			self.rect = self.image.get_rect(center=center)
