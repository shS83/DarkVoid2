import pygame as pg


class Series_of_Explosions(pg.sprite.Sprite):
	def __init__(self, game, pos):
		super().__init__()

		self.game = game
		self.frames = self.game.explosion_frames
		self.index = 0
		self.index2 = 0
		self.timer = 0
		self.timer2 = 0
		self.frame_time = 0.045
		self.frame_time2 = 0.02

		self.image = self.frames[self.index]
		self.image2 = self.frames[self.index2]
		self.rect = self.image.get_rect(center=pos)
		self.rect2 = self.image.get_rect(center=pos)

	def update(self, dt):
		self.timer += dt
		self.timer2 += dt

		if self.timer >= self.frame_time:
			self.timer = 0
			self.index += 1

		if self.timer2 >= self.frame_time2:
			self.timer2 = 0
			self.index2 += 1

			if self.index >= len(self.frames) and self.index2 >= len(self.frames):
				self.kill()
				return

			center = self.rect.center
			center2 = self.rect2.midtop
			try:
				if self.index <= len(self.frames) and self.index2 <= len(self.frames):
					self.image = self.frames[self.index]
					self.image2 = self.frames[self.index2]
					self.rect = self.image.get_rect(center=center)
					self.rect2 = self.image2.get_rect(midtop=center2)
			except IndexError:
				print("boohoo")


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
