from core.gameobject import GameObject
import pygame as pg


class Bullet(GameObject):
	def __init__(self, position, velocity):
		image = pg.Surface((6, 12))
		image.fill((255, 255, 0))

		super().__init__(position, image, velocity)

	def update(self, dt):
		super().update(dt)

		if not pg.display.get_surface().get_rect().collidepoint(self.position):
			self.kill()
