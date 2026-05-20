import pygame as pg
import random
import os
from pygame.transform import rotozoom
from game import Game

pg.init()
timer = pg.time.Clock()
# fonts = ['arial black', 'constantia', 'warheliosconcbold', 'averiasansbold', 'goodtimes', 'prceltic', 'novaround', 'xfiles']

x_res = 1920
y_res = 1080
screen = pg.display.set_mode((x_res, y_res), pg.SRCALPHA, 32)
HOME = "/home/shs/PycharmProjects/DarkVoid2"
HOME_DIR = HOME
pg.event.clear()
pg.mixer.music.load(f'{HOME_DIR}/assets/Ov Moi Omm - The Dictator’s Transmission (YSMHB).mp3')
pg.mixer.music.play(-1)
pg.mixer.init(48000, -16, 2, 4096)
pg.mixer.music.set_volume(0.2)
pg.mixer.set_num_channels(32)
font_size = 200
fontti = pg.font.Font(f'{HOME_DIR}/assets/VL-Gothic-Regular.ttf', font_size)
textfont = pg.font.Font(f'{HOME_DIR}/assets/GoMonoNerdFontPropo-Bold.ttf', 200)
fonts = ['prceltic', fontti, textfont]
pg.display.set_icon(fontti.render("シ", True, (0, 255, 0)))
font = pg.font.SysFont(fonts[0], 72)
# font = pg.font.SysFont('msgothic', 72)
font2 = pg.font.SysFont('msgothic', 48)
screen.blit(fontti.render("シ", True, (255, 255, 255)), (screen.get_width() // 2, screen.get_height() // 2))
running = True
cooldown = 500
switch = True
i = 0
last = 0
logointerval = 200
pg.display.set_caption("Dark Void 2 - The Voidling")
INITEVENT = pg.USEREVENT + 1
pg.time.set_timer(INITEVENT, 5000, 20000)
screen.blit(rotozoom(textfont.render("DARK VOID 2", True, (255, 255, 255)), 3.0, 1.3), (100, 300), (0, 0, x_res, y_res))
pg.display.flip()
timer.tick(159)
xd2, yd2 = font2.size("press space to continue")
f = 0
finished = True
in_logo = False
begin = False
LOGOEVENT = pg.USEREVENT + 2
pg.event.post(pg.event.Event(LOGOEVENT))

pg.time.set_timer(LOGOEVENT, 1000, 2000)
FADEOUTEVENT = pg.USEREVENT + 3
pg.time.set_timer(FADEOUTEVENT, 1000, 2000)
INITGAME = pg.USEREVENT + 4

pg.event.post(pg.event.Event(LOGOEVENT))

while running:

	for event in pg.event.get():

		if event.type == pg.QUIT:
			running = True

		if event.type == pg.KEYDOWN:
			if event.key == pg.K_ESCAPE:
				running = False
			if in_logo and event.key == pg.K_SPACE:
				print("space pressed")

				# pg.event.clear()
				in_logo = True

				pg.event.post(pg.event.Event(INITGAME))

		if event.type == INITEVENT and i < 255:
			now = pg.time.get_ticks()
			if now - last >= cooldown:
				last = now
			screen.fill((0, 0, 0))
			screen.blit(textfont.render("DARK VOID 2", True, (i, 0, 0)),
			            (x_res / 2 / 2, y_res / 2 / 2))
			screen.blit(fontti.render("ヾ", True, (255, 255, 255)),
			            (screen.get_width() // 2, screen.get_height() // 2))
			i += 1
			if i > 254:
				i = 255
				# print("init anim finished")
				pg.event.clear()
				in_logo = True
				last = 0

			pg.event.post(pg.event.Event(INITEVENT))

		if event.type == LOGOEVENT:
			if in_logo:
				now = pg.time.get_ticks()

				# if now - last >= logointerval:
				# 	last = now
				#	switch = True
				screen.fill((0, 0, 0))
				# screen.blit(fontti.render("ヾ", True, (255, 255, 255)),
				#           (screen.get_width() // 2, screen.get_height() // 2))
				# if switch:
				screen.blit(pg.image.load(f'{HOME_DIR}/assets/stimu_wallpaper.png'), (0, 0))
				# screen.blit(textfont.render("DARK VOID 2", True, (i, 0, 0)),
				# 	            (x_res / 2 - xd2 / 2, y_res / 2 - yd2 / 2))
				# 	screen.blit(font2.render("press space to continue", True, (255, 0, 0)),
				# 	            (x_res / 2 - xd2 / 2, y_res - yd2 * 2))
				# else:
				# 	screen.blit(textfont.render("DARK VOID 2", True, (i, 0, 0)),
				# 	            (x_res / 2 - xd2 / 2, y_res / 2 - yd2 / 2))
				pg.event.post(pg.event.Event(LOGOEVENT))

		if event.type == FADEOUTEVENT:
			in_logo = False
			if i > 1:
				now = pg.time.get_ticks()
				if now - last >= cooldown:
					screen.fill((0, 0, 0))
					screen.blit(textfont.render("DARK VOID 2", True, (i, 0, 0)),
					            (x_res / 2 - xd2 / 2, y_res / 2 - yd2 / 2))
					i -= 2
					if i < 2:
						print("fadeout anim finished")
						pg.event.clear()
						pg.event.post(pg.event.Event(INITGAME))
				pg.event.post(pg.event.Event(FADEOUTEVENT))

		if event.type == INITGAME:
			finished = True
			running = False
			print("game initialized")
			Game().run()
	# MAIN LOOP

	pg.display.flip()
	timer.tick(159)
