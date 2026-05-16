from core.config import commons as c
import pygame as pg
import sys

clock = pg.time.Clock()
running = True
while running:
	c.screen = pg.display.set_mode((1920, 1080), pg.SRCALPHA)
	c.screen.fill((0, 0, 10))
	dt = clock.tick(60) / 1000
	all_sprites.update(dt)

	pg.display.flip()
	c.screen.blit(c.BACKGROUND, (0, 0))
	keys = pg.key.get_pressed()
	mouse = pg.mouse.get_pressed()
	if keys[K_ESCAPE]:
		c.running = False

	if keys[K_RETURN]:
		pg.mixer.Sound(f'{c.HOME_DIR}/assets/lasersound.wav').play()
		enterprise.shoot_guns(c.ship_x, c.ship_y)

	# Direct key input (no delay check needed for responsive 1942-style movement)
	if keys[pg.K_UP] or keys[pg.K_w]:
		enterprise.strafe_y(-5)  # UP = negative Y
	if keys[pg.K_DOWN] or keys[pg.K_s]:
		enterprise.strafe_y(5)  # DOWN = positive Y
	if keys[pg.K_LEFT] or keys[pg.K_a]:
		draw_left()  # Tilt animation flick
		enterprise.strafe_x(-5)  # LEFT = negative X
	if keys[pg.K_RIGHT] or keys[pg.K_d]:
		draw_right()
		enterprise.strafe_x(5)  # RIGHT = positive X
	if keys[pg.K_SPACE]:
		c.laserkey += 1
	if c.laserkey > c.laserinterval:
		pg.mixer.Sound(f'{c.HOME_DIR}/assets/lasersound.wav').play()
		enterprise.shoot_guns(c.ship_x, c.ship_y)
		random.choice([pg.mixer.Sound(f'{c.HOME_DIR}/assets/boom.wav').play(),
		               pg.mixer.Sound(f'{c.HOME_DIR}/assets/boom4.wav').play()])

	if not enterprise and c.message == "YOU DIED":
		State = State.DIED_WATCHING_ROCKS
		once = True
		pg.event.clear()

	if not asteroids and enterprise and enterprise.visible:
		c.lvl_timer = pg.time.get_ticks()
		once = False
		c.message = "ENEMIES FELLED"
		pg.mixer.Sound(f'{c.HOME_DIR}/assets/levelup.wav').play()
		c.msg_opacity = 255
		c.msg_rot = 1
		c.msg_sca = 1
		c.now = pg.time.get_ticks()
		State = State.NEXTLEVEL
		if c.now > c.lvl_timer + 2000:
			c.message = ""
			once = True
			enterprise.visible = False
			level.up()
			pg.event.clear()

	for game_object in _get_game_objects():

		if game_object is None:
			del game_object
			continue
		if isinstance(int, (str(game_object))):
			del game_object
			continue
		if hasattr(game_object, 'rotate_in_place'):
			game_object.rotate_in_place()
		if hasattr(game_object, 'move'):
			game_object.move(c.screen)
		if not hasattr(game_object, 'position') or not hasattr(game_object, 'draw'):
			c.screen.blit(game_object.sprite, game_object.position)
		else:
			c.screen.blit(game_object.sprite, game_object.position)

	screen.blit(render_char("DarkVoid2 beta 0.0149", (100, 100, 255)), (10, 10))
	screen.blit(render_char(f"Asteroids: {len(asteroids_group)}", (100, 255, 100)), (10, 50))
	pg.display.flip()

	enterprise.update()
	enterprise.draw(screen)

	if isinstance(game_object, Star):
		continue
	if game_object is None:
		del game_object
		continue
	if isinstance(int, (str(game_object))):
		del game_object
		continue
	if hasattr(game_object, 'rotate_in_place'):
		game_object.rotate_in_place()
	if hasattr(game_object, 'move'):
		game_object.move(c.screen)
	if not hasattr(game_object, 'sprite'):
		continue
	c.screen.blit(game_object.sprite, game_object.position)

pg.mixer.fadeout(2000)
pg.mixer.stop()
pg.quit()
sys.exit()
