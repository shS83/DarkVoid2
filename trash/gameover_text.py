from core.utils import zoom_text
from core import commons as c
from pygame.transform import rotozoom


class Gameover:
	def __init__(self):
		self.zoomfont = c.msg_font
		self.msg = "GAME OVER"
		self.color = (255, 0, 0)
		self.opacity = 255
		self.rot = 6.00
		self.sca = 6.00
		self.timer = 30.00

	def draw(self, screen):
		fs = self.zoomfont.render(self.msg, True, self.color)
		rotated = rotozoom(fs, self.rot, self.sca)
		rotated.set_alpha(self.opacity)
		xd = rotated.get_width()
		yd = rotated.get_height()
		screen.blit(rotated, (c.x_res // 2, c.y_res // 2))
		return rotated, c.x_res / 2 - xd / 2, c.y_res / 2 - yd / 2

	def update(self, dt):
		self.sca -= dt * 0.005
		self.rot -= dt * 0.005
		self.opacity -= dt * 0.005
		self.timer -= dt
		if self.timer <= 0:
			return True
