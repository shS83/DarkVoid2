import pygame as pg
import random
import os
from pygame.transform import rotozoom
from game import Game
from time import sleep

pg.init()
timer = pg.time.Clock()
# fonts = ['arial black', 'constantia', 'warheliosconcbold', 'averiasansbold', 'goodtimes', 'prceltic', 'novaround', 'xfiles']

x_res = 1920
y_res = 1080
screen = pg.display.set_mode((x_res, y_res), pg.SRCALPHA, 32)
HOME_DIR = os.path.dirname(__file__).replace('/core', '')
print(HOME_DIR)
screen.blit(pg.image.load(f'{HOME_DIR}/assets/stimu_wallpaper.png'), (0, 0))
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
font = pg.font.SysFont(fonts[0], 36)
# font = pg.font.SysFont('msgothic', 72)
font2 = pg.font.SysFont('msgothic', 48)
screen.blit(fontti.render("シ", True, (255, 255, 255)), (screen.get_width() // 2, screen.get_height() // 2))
running = True
cooldown = 500
switch = True
i = 0
last = 0
logointerval = 500
pg.display.set_caption("Dark Void 2 - The Avoided")
INITEVENT = pg.USEREVENT + 1
pg.time.set_timer(INITEVENT, 5000, 20000)
surf = pg.surface.Surface((1920, 1080), pg.SRCALPHA, 32).convert_alpha()
surf.fill(
	(0, 0, 0, 255)
)
pg.display.flip()
sleep(2)
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
				running = False

				pg.event.clear()
				in_logo = True
				i = 100
				pg.event.post(pg.event.Event(LOGOEVENT))

		if event.type == LOGOEVENT:
			direction = 1
			i = 255
			i += -direction
			direction = 1
			if i < 1:
				direction = -direction
			now = pg.time.get_ticks()
			if now - last >= cooldown:
				last = now
			screen.fill((0, 0, 0))
			screen.blit(textfont.render("DARK VOID 2", True, (i, 0, 0)),
			            (x_res / 2 / 2, y_res / 2 / 2))
			screen.blit(fontti.render("ヾ", True, (255, 255, 255)),
			            (screen.get_width() // 2, screen.get_height() // 2))
			screen.blit(textfont.render("The AVOiDED", True, (255, 0, 0)), (x_res / 2 / 2, y_res / 2 + 120))
			screen.blit(font.render("press ESC to avoid...", True, (255, 200, 255)), (x_res /2 / 2-100, y_res / 2 + 400))
			pg.event.post(pg.event.Event(LOGOEVENT))

		if event.type == LOGOEVENT:
			if in_logo:
				now = pg.time.get_ticks()
				screen.fill((0, 0, 0))
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
						pg.event.clear()
						pg.event.post(pg.event.Event(INITGAME))

		if event.type == INITGAME:
			finished = True
			running = False

	pg.display.flip()
	dt = timer.tick(60) / 1000
Game().run()
