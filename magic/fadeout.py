import pygame as pg


class Fadeout:
	""" Fadeout unto darkness """

	def __init__(self, obj: pg.Surface, delay: float):
		self.object = obj
		self.delay = delay
		self.alpha = 255

	def fade_out(self) -> pg.Surface:
		if (self.delay <= 0) and (self.alpha > 0):
			self.alpha -= 1
			self.object.set_alpha(self.alpha)
		self.delay -= 1
		return self.object.copy()
