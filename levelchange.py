import pygame, pygame.gfxdraw, random, math
from darkvoid2 import BACKGROUND, ASTEROIDS, ROCK_IMAGES, ROCK1, ROCK2, ROCK3, ROCK4

x_res = 1920
y_res = 1080
NOW_MS = 0
timer = pygame.time.Clock()
pygame.init()
screen = pygame.display.set_mode([x_res, y_res], pygame.SHOWN)
startTime = pygame.time.get_ticks()
font = pygame.font.SysFont('msgothic', 36)
infofont = pygame.font.SysFont('msgothic', 18)
running = True
rot = 1
sca = 1
opacity = 255


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


LEVELCHANGE = pygame.USEREVENT + 5
# levels start at +7
LEVEL = pygame.USEREVENT + 7
# and more +8 ->
GAME = pygame.USEREVENT + 6


def zoom_text(msg, color, opacity, rot=1.00, sca=1.00):
	fs = font.render(msg, True, color)
	rotated = pygame.transform.rotozoom(fs, rot, sca)
	rotated.set_alpha(opacity)
	xd = rotated.get_width()
	yd = rotated.get_height()
	screen.blit(rotated, (x_res / 2 - xd / 2, y_res / 2 - yd / 2))


level = Level()
pygame.event.post(pygame.event.Event(LEVELCHANGE))
while running:

	screen.fill((0, 0, 15))
	screen.blit(BACKGROUND, (0, 0))

	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
			running = False
		if event.type == pygame.QUIT:
			running = False

		if event.type == pygame.KEYDOWN and event.key == pygame.K_KP_PLUS:
			opacity = 255
			rot = 1
			sca = 1
			level.up()
			pygame.event.clear()
			print(LEVEL + level.stage)
			pygame.event.post(pygame.event.Event(LEVELCHANGE))

		if event.type == LEVELCHANGE:
			TEXT = f"LEVEL {level.stage}"
			if opacity > 1:
				zoom_text(TEXT, (255, 0, 0), opacity, rot, sca)
				opacity -= 1.5
				rot += 0.15
				sca += 0.01
				pygame.event.post(pygame.event.Event(LEVELCHANGE))
			else:
				opacity = 255
				rot = 1
				sca = 1
				pygame.event.clear()
				print(LEVEL + level.stage)
				pygame.event.post(pygame.event.Event(LEVEL + level.stage))
				level.up()

		if event.type == LEVEL + level.stage:
			TEXT = "START"
			if opacity > 1:
				zoom_text(TEXT, (0, 255, 0), opacity, rot, sca)
				opacity -= 4
				sca += 0.05
				print(LEVEL + level.stage)
				pygame.event.post(pygame.event.Event(LEVEL + level.stage))
			else:
				pygame.event.post(pygame.event.Event(GAME))

		if event.type == GAME:
			print("game")

	info1 = infofont.render(f"level: {level.stage}, rocks: {level.asteroids}", True, (255, 255, 255))
	info2 = infofont.render(f"ast_speed: {level.asteroid_speed}, ast_hp: {level.asteroid_hp}", True, (255, 255, 255))
	screen.blit(info1, (30, 30))
	screen.blit(info2, (30, 50))
	pygame.display.flip()
	timer.tick(120)
