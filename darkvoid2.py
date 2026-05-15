import pygame as pg
from pygame.locals import *
# import intro_module
import pygame.mixer
import random
from core.spritegroups import particles_group, asteroid_group, bullet_group, star_group
from entities.level import Level
from entities.states import State
from core import commons
from entities.ship import enterprise
from core.utils import zoom_text

level = Level()
c.running = True
c.clock = pg.time.Clock()
while c.running:
	zoom_text("DARK VOID 2", (255, 255, 255), 255, rot=0.00, sca=4.0)
	curr_state = State.INTRO

	key = pg.key.get_pressed()

	enterprise.update(c.screen)
	enterprise.draw(c.screen)

	c.collidetime = pg.time.get_ticks()
	c.collision_delay = 150
	c.now = pygame.time.get_ticks()
	if c.now > c.collidetime + c.collision_delay:
		for rock, asteroid in asteroids_group:
			if rock.collides_with_tolerance(asteroid, -15):
				temp = asteroid.velocity
				asteroid.velocity = rock.velocity
				asteroid.rotdelta = -asteroid.rotdelta
				asteroid.position = wrap_position(asteroid.position + asteroid.velocity * 2, c.screen)
				rock.velocity = temp
				rock.position = wrap_position(rock.position + rock.velocity * 2, c.screen)
				c.collidetime = pg.time.get_ticks()
				break

	for bullet in bullet_group:
		for asteroid in asteroid_group:
			if asteroid.collides_with(bullet):
				random.choice([pg.mixer.Sound(f'{c.HOME_DIR}/assets/boom2.wav').play(),
				               pg.mixer.Sound(f'{c.HOME_DIR}/assets/boom4.wav').play()])
				asteroid.hp -= 1

	for bullet in bullet_group:
		if not c.screen.get_rect().collidepoint(bullet.position):
			bullet_group.remove(bullet)
