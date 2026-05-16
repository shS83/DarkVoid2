import pygame as pg
import config as c
from entities.bullet import PlayerBullet


class Player(pg.sprite.Sprite):
	def __init__(self, game, pos):
		super().__init__()
		self.game = game
		# self.image = pg.Surface((42, 52), pg.SRCALPHA)
		# pg.draw.polygon(self.image, (220, 220, 255), [(21, 0), (42, 52), (21, 42), (0, 52)])
		self.image = pg.image.load("assets/Proper_warship.png").convert_alpha()
		self.rect = self.image.get_rect(center=pos)
		self.pos = pg.Vector2(pos)
		self.fire_timer = 0
		self.alive = True
		self.invuln = 0

	def update(self, dt):
		keys = pg.key.get_pressed()
		direction = pg.Vector2(0, 0)

		if keys[pg.K_LEFT] or keys[pg.K_a]:
			direction.x -= 1
		if keys[pg.K_RIGHT] or keys[pg.K_d]:
			direction.x += 1
		if keys[pg.K_UP] or keys[pg.K_w]:
			direction.y -= 1
		if keys[pg.K_DOWN] or keys[pg.K_s]:
			direction.y += 1

		if direction.length_squared() > 0:
			direction = direction.normalize()

		focused = keys[pg.K_LSHIFT] or keys[pg.K_RSHIFT]
		speed = c.PLAYER_FOCUS_SPEED if focused else c.PLAYER_SPEED
		self.pos += direction * speed * dt

		self.pos.x = max(20, min(c.WIDTH - 20, self.pos.x))
		self.pos.y = max(20, min(c.HEIGHT - 20, self.pos.y))
		self.rect.center = self.pos

		self.fire_timer -= dt
		if keys[pg.K_z] or keys[pg.K_SPACE]:
			self.shoot()

		if self.invuln > 0:
			self.invuln -= dt

	def shoot(self):
		if self.fire_timer > 0:
			return

		self.fire_timer = c.PLAYER_FIRE_COOLDOWN
		offsets = [-10, 10]
		for ox in offsets:
			bullet = PlayerBullet(self.game, (self.pos.x + ox, self.pos.y - 24))
			self.game.player_bullets.add(bullet)
			self.game.all_sprites.add(bullet)
