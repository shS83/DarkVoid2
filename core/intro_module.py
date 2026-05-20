import pygame, random, os
from pygame.transform import rotozoom

pygame.init()
timer = pygame.time.Clock()
# fonts = ['arial black', 'constantia', 'warheliosconcbold', 'averiasansbold', 'goodtimes', 'prceltic', 'novaround', 'xfiles']
fonts = ['prceltic']
x_res = 1920
y_res = 1080
screen = pygame.display.set_mode([x_res, y_res], pygame.SHOWN)
HOME_DIR = os.path.expanduser('~') + '/PycharmProjects/DarkVoid2'
pygame.event.clear()

font_size = 200
fontti = pygame.font.Font(f'{HOME_DIR}/assets/VL-Gothic-Regular.ttf', font_size)
textfont = pygame.font.Font(f'{HOME_DIR}/assets/GoMonoNerdFontPropo-Bold.ttf', 200)
pygame.display.set_icon(fontti.render("シ", True, (0, 255, 0)))
font = pygame.font.SysFont(fonts[0], 72)
# font = pygame.font.SysFont('msgothic', 72)
font2 = pygame.font.SysFont('msgothic', 48)
screen.blit(fontti.render("シ", True, (255, 255, 255)), (screen.get_width() // 2, screen.get_height() // 2))
running = True
cooldown = 500
switch = True
i = 0
last = 0
logointerval = 200
screen = pygame.display.set_mode([x_res, y_res], pygame.SHOWN)
pygame.display.set_caption("Dark Void 2 - The Voidling")
INITEVENT = pygame.USEREVENT + 1
pygame.time.set_timer(INITEVENT, 5000, 20000)
screen.blit(rotozoom(textfont.render("DARK VOID 2", True, (255, 255, 255)), 3.0, 1.3), (100, 300), (0, 0, x_res, y_res))
pygame.display.flip()
timer.tick(159)
xd2, yd2 = font2.size("press space to continue")
f = 0
finished = True
in_logo = False
begin = False
LOGOEVENT = pygame.USEREVENT + 2
pygame.event.post(pygame.event.Event(LOGOEVENT))

pygame.time.set_timer(LOGOEVENT, 1000, 2000)
FADEOUTEVENT = pygame.USEREVENT + 3
pygame.time.set_timer(FADEOUTEVENT, 1000, 2000)
INITGAME = pygame.USEREVENT + 4

pygame.event.post(pygame.event.Event(LOGOEVENT))

while running:

	for event in pygame.event.get():

		if event.type == pygame.QUIT:
			running = True

		if event.type == pygame.KEYDOWN:

			if in_logo and event.key == pygame.K_SPACE:
				print("space pressed")

				# pygame.event.clear()
				in_logo = True

				pygame.event.post(pygame.event.Event(INITGAME))

		if event.type == INITEVENT and i < 255:
			now = pygame.time.get_ticks()
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
				pygame.event.clear()
				in_logo = True
				last = 0

			pygame.event.post(pygame.event.Event(INITEVENT))

		if event.type == LOGOEVENT:
			if in_logo:
				now = pygame.time.get_ticks()

				if now - last >= logointerval:
					last = now
					switch = True
					screen.fill((0, 0, 0))
					screen.blit(fontti.render("ヾ", True, (255, 255, 255)),
					            (screen.get_width() // 2, screen.get_height() // 2))
					if switch:
						screen.blit(pygame.image.load(f'{HOME_DIR}/assets/stimu_wallpaper.png'), (0, 0))
						screen.blit(textfont.render("DARK VOID 2", True, (i, 0, 0)),
						            (x_res / 2 - xd2 / 2, y_res / 2 - yd2 / 2))
						screen.blit(font2.render("press space to continue", True, (255, 0, 0)),
						            (x_res / 2 - xd2 / 2, y_res - yd2 * 2))
					else:
						screen.blit(textfont.render("DARK VOID 2", True, (i, 0, 0)),
						            (x_res / 2 - xd2 / 2, y_res / 2 - yd2 / 2))
				pygame.event.post(pygame.event.Event(LOGOEVENT))

		if event.type == FADEOUTEVENT:
			in_logo = False
			if i > 1:
				now = pygame.time.get_ticks()
				if now - last >= cooldown:
					screen.fill((0, 0, 0))
					screen.blit(textfont.render("DARK VOID 2", True, (i, 0, 0)),
					            (x_res / 2 - xd2 / 2, y_res / 2 - yd2 / 2))
					i -= 2
					if i < 2:
						print("fadeout anim finished")
						pygame.event.clear()
						pygame.event.post(pygame.event.Event(INITGAME))
				pygame.event.post(pygame.event.Event(FADEOUTEVENT))

		if event.type == INITGAME:
			finished = True
			running = False
			print("game initialized")

	# MAIN LOOP

	pygame.display.flip()
	timer.tick(159)
