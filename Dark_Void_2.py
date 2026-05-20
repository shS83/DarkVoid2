import pygame as pg
import os
from entities.level import *
from entities.states import *
from entities.events import *
from core.utils import *
from magic.colors import *
import time
from pygame.transform import rotozoom


# from entities.stars import roll_the_drops, starfield, starfields


class Dark_Void_2(pg.sprite.Sprite):
	def __init__(self, game):
		super().__init__()
		self.game = game
		pg.mixer.music.load(
			f'{c.HOME_DIR}/assets/Ov Moi Omm - The Dictator’s Transmission (YSMHB).mp3')
		pg.mixer.init(48000, -16, 2, 4096)
		pg.mixer.music.play(-1)
		pg.mixer.music.set_volume(0.2)
		Status = State.INTRO
		# from core import intro_module

		self.screen = pg.display.set_mode((1920, 1080), pg.SRCALPHA)
		Status = State.WAITINGFORGAME
		Stage = Level()

		pg.display.set_caption("DARK VOID 2")
		clock = pg.time.Clock()
		running = True

		def update(dt):
			...

		def draw(screen):
			...

		def spawn_rock(screen):
			#		self.asteroids.add(Asteroid(self, 100, 100))
			...

		while running:
			dt = clock.tick(60) / 1000
			self.screen.fill((0, 0, 10))
			# if Event == 1:

			# self.spawn_rock(self.screen)
			# else:
			x_res, y_res = 1920, 1080
			textfont = pg.font.Font(f'{c.HOME_DIR}/assets/JetBrainsMonoNerdFont-SemiBold.ttf', 200)

			self.screen.blit(rotozoom(textfont.render(r" ⯗ ", True, (255, 255, 255)), 1.5, 2.3), (300, 500))

			time.sleep(5)
			pg.display.flip()
			self.screen.blit(rotozoom(textfont.render(r" ࿐ ", True, (181, 101, 220)), 3.0, 4.3), (400, 550))

			time.sleep(5)

			pg.display.flip()
