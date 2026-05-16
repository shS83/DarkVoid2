import pygame as pg
import config as c
from entities.bullet import PlayerBullet


class Player(pg.sprite.Sprite):
	def __init__(self, game, pos):
		super().__init__()
		self.fire_timer = 0
		self.fire_cooldown = 0.12
		self.game = game
		self.image = pg.image.load("assets/Proper_warship.png").convert_alpha()
		self.image = pg.transform.scale(self.image, (96, 96))
		self.rect = self.image.get_rect(center=pos)
		self.pos = pg.Vector2(self.rect.center)
		self.speed = 350

	def shoot(self):
		if self.fire_timer > 0:
			return

		self.fire_timer = self.fire_cooldown
		bullet = PlayerBullet(self.game, self.rect.midtop)
		self.game.player_bullets.add(bullet)
		self.game.all_sprites.add(bullet)
		
	def update(self, dt):
		keys = pg.key.get_pressed()
		mouse = pg.mouse.get_pressed()
		direction = pg.Vector2(0, 0)
		self.fire_timer -= dt
		if keys[pg.K_LEFT] or keys[pg.K_a]:
			direction.x -= 1
		if keys[pg.K_RIGHT] or keys[pg.K_d]:
			direction.x += 1
		if keys[pg.K_UP] or keys[pg.K_w]:
			direction.y -= 1
		if keys[pg.K_DOWN] or keys[pg.K_s]:
			direction.y += 1
		if keys[pg.K_SPACE] or mouse[0]:
			self.shoot()
		if direction.length_squared() > 0:
			direction = direction.normalize()

		self.pos += direction * self.speed * dt

		self.pos.x = max(32, min(c.WIDTH - 32, self.pos.x))
		self.pos.y = max(32, min(c.HEIGHT - 32, self.pos.y))

		self.rect.center = self.pos
