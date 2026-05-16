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


class Dark_Void_2:
	def run(self):
		pg.mixer.music.load(
			f'{os.getcwd()}/assets/Ov Moi Omm - The Dictator’s Transmission (YSMHB).mp3')
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

		while running:
			dt = clock.tick(60) / 1000
			self.screen.fill((0, 0, 10))
			# if Event == 1:

			spawn_rock(self.screen)
			# else:
			x_res, y_res = 1920, 1080
			textfont = pg.font.Font(f'{os.getcwd()}/assets/JetBrainsMonoNerdFont-SemiBold.ttf', 200)

			self.screen.blit(rotozoom(textfont.render(r" ⯗ ", True, (255, 255, 255)), 1.5, 2.3), (300, 500))

			time.sleep(5)
			pg.display.flip()
			self.screen.blit(rotozoom(textfont.render(r" ࿐ ", True, (181, 101, 220)), 3.0, 4.3), (400, 550))

			time.sleep(5)

			pg.display.flip()
