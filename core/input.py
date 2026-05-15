import pygame as pg


class Input:
	def __init__(self):
		self.keys = None

	def update(self):
		self.keys = pg.key.get_pressed()

	def pressed(self, key):
		return self.keys[key]

	input_handler = Input()
	input_handler.update()

	if input_handler.pressed(pg.K_LEFT):
		ship.rotate_left()
