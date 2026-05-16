import pygame, pygame.gfxdraw

x_res = 1920
y_res = 1080
NOW_MS = 0
timer = pygame.time.Clock()
pygame.init()
# screen = pygame.display.set_mode([x_rES, y_res], pygame.SHOWN)
startTime = pygame.time.get_ticks()
font = pygame.font.SysFont('msgothic', 36)
infofont = pygame.font.SysFont('msgothic', 18)
running = True
rot = 1
sca = 1
opacity = 255


class Platform:
	def __init__(self, stage=1, asteroids=7, asteroid_speed=1, asteroid_hp=1):
		self.stage = 1
		self.asteroids = 7
		self.asteroid_speed = 1
		self.asteroid_hp = 1

	def up(self):
		self.stage += 1
		self.asteroids += 1
		self.asteroid_speed += 0.20
		self.asteroid_hp += 0.20


LEVELCHANGE = pygame.USEREVENT + 5
# levels start at +7
LEVEL = pygame.USEREVENT + 7
# and more +8 ->
GAME = pygame.USEREVENT + 6


def zoom_text(screen, msg, color, opacity, rot=1.00, sca=1.00):
	fs = font.render(msg, True, color)
	rotated = pygame.transform.rotozoom(fs, rot, sca)
	rotated.set_alpha(opacity)
	xd = rotated.get_width()
	yd = rotated.get_height()
	screen.blit(rotated, (x_res / 2 - xd / 2, y_res / 2 - yd / 2))
