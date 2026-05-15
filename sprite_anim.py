import pygame, pygame.gfxdraw, random, math, os

x_res = 1920
y_res = 1080
NOW_MS = 0
timer = pygame.time.Clock()
pygame.init()
screen = pygame.display.set_mode([x_res, y_res], pygame.SHOWN)
startTime = pygame.time.get_ticks()
running = True

LEVELCHANGE = pygame.USEREVENT + 5
HOME_DIR = os.path.expanduser('~') + '/PycharmProjects/DarkVoid2'
rightship = []
leftship = []
midship = []
current_frame = 1
last = 0


def loadsprite_1():
	frames = 4
	for i in range(1, frames + 1):
		img = pygame.image.load(f'{HOME_DIR}/assets/ship_right_{i}.png').convert_alpha()
		rightship.append(img)


def loadsprite_2():
	frames = 4
	for i in range(1, frames + 1):
		img = pygame.image.load(f'{HOME_DIR}/assets/ship_left_{i}.png').convert_alpha()
		leftship.append(img)


def draw_anim(screen, spritegroup, pos, interval, repeat=False):
	global current_frame, last
	NOW = pygame.time.get_ticks()
	anim_length = len(spritegroup)
	if not repeat and current_frame >= anim_length:
		screen.fill((0, 0, 0))
		pygame.display.flip()
		return True
	if repeat and current_frame >= anim_length:
		current_frame = 1
	if NOW > last + interval:
		last = NOW
		screen.fill((0, 0, 0))
		screen.blit(spritegroup[current_frame], pos)
		current_frame += 1
		pygame.display.flip()
		timer.tick(159)
	draw_anim(screen, midship, (100, 100), interval=4, repeat=False)
	return False


loadsprite_1()
loadsprite_2()


# screen.fill((0, 0, 0))

# def draw_left(screen, pos, rot, sca):
#    screen.blit(leftship[current_frame], (pos[0] * sca, pos[1] * sca), (0, 0, leftship[current_frame].get_width() * sca, leftship[current_frame].get_height() * sca), rot)
def draw_left():
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
			running = False
		if event.type == pygame.QUIT:
			running = False
	midship = leftship.copy()
	draw_anim(screen, midship, (100, 100), 4, False)


def draw_right():
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
			running = False
		if event.type == pygame.QUIT:
			running = False
	midship = rightship.copy()
	draw_anim(screen, midship, (100, 100), 4, False)
