import random
from icecream import ic
import pygame as pg
import config as c
from pathlib import Path
from entities.glitter import Glitter
c.HOME_DIR = Path(__file__).parent.parent.absolute()

class PlayerBullet(pg.sprite.Sprite):
	def __init__(self, game, pos, image=pg.image.load(c.resource_path(Path(c.HOME_DIR, "assets", "laser.png"))).convert_alpha(), velocity=(0, -800)):
		super().__init__()
		self.image = image
		self.game = game
		self.pos = pg.Vector2(pos)
		self.rect = self.image.get_rect(center=self.pos)
		self.velocity = pg.Vector2(velocity)
		self.damage = 1
		self.mask = pg.mask.from_surface(self.image)

	def update(self, dt = pg.time.Clock().tick(60)/1000):
		self.pos += self.velocity * dt
		self.rect.center = self.pos

		if self.rect.bottom < 0 or self.rect.top > c.HEIGHT or self.rect.left < 0 or self.rect.right > c.WIDTH:
			self.kill()


class EnemyBullet(pg.sprite.Sprite):

	frames = None

	def __init__(self, game, pos, velocity):
		super().__init__()
		self.colors = {"RED": [255, 0, 0],
		               "GREEN": [0, 255, 0],
		               "BLUE": [0, 0, 255],
		               "WHITE": [255, 255, 255],
		               "BLACK": [0, 0, 0],
		               "YELLOW": [255, 255, 0],
		               "MAGENTA": [255, 0, 255],
		               "CYAN": [0, 255, 255],
		               "ORANGE": [255, 115, 0],
		               "LIME": [128, 255, 0],
		               "PEACH": [255, 200, 128],
		               "PURPLE": [128, 0, 128],
		               "PINK": [255, 128, 255],
		               }
		self.game = game
		self.pos = pg.Vector2(pos)
		self.velocity = pg.Vector2(velocity)

		# Actual fair hitbox, not visual size
		self.radius = 6

		if EnemyBullet.frames is None:
			EnemyBullet.frames = self.make_bullet_frames()

		self.frame_index = 0
		self.anim_timer = 0
		self.anim_speed = 0.045

		self.image = EnemyBullet.frames[self.frame_index]
		self.rect = self.image.get_rect(center=self.pos)

	def make_bullet_frames(self):
		frames = []

		for frame in range(4):
			size = 46
			center = size // 2
			image = pg.Surface((size, size), pg.SRCALPHA)

			pulse = frame / 3

			outer_color = (255, 120, 10)
			mid_color = (255, 210, 40)
			# core_color = (255, 255, 210)
			core_color = random.choice(list(self.colors.values()))

			max_radius = 22

			for radius in range(max_radius, 0, -1):
				t = 1 - radius / max_radius

				if t < 0.55:
					local_t = t / 0.55
					r = self.lerp(outer_color[0], mid_color[0], local_t)
					g = self.lerp(outer_color[1], mid_color[1], local_t)
					b = self.lerp(outer_color[2], mid_color[2], local_t)
				else:
					local_t = (t - 0.55) / 0.45
					r = self.lerp(mid_color[0], core_color[0], local_t)
					g = self.lerp(mid_color[1], core_color[1], local_t)
					b = self.lerp(mid_color[2], core_color[2], local_t)

				alpha = int(10 + 180 * (t ** 2))
				alpha += int(25 * pulse)

				pg.draw.circle(
					image,
					(int(r), int(g), int(b), min(255, alpha)),
					(center, center),
					radius
				)

			# Hot core
			pg.draw.circle(image, (255, 245, 110, 255), (center, center), 7)
			pg.draw.circle(image, (255, 90, 40, 255), (center, center), 5)
			pg.draw.circle(image, (255, 255, 230, 255), (center - 1, center - 1), 3)

			# Small specular glint, so it feels like energy/plasma, not a flat dot
			pg.draw.circle(image, (255, 255, 255, 210), (center - 4, center - 5), 2)

			frames.append(image)

		return frames

	def lerp(self, a, b, t):
		return a + (b - a) * t

	def update(self, dt):
		self.pos += self.velocity * dt
		self.rect.center = self.pos

		self.anim_timer += dt

		if self.anim_timer >= self.anim_speed:
			self.anim_timer = 0
			self.frame_index = (self.frame_index + 1) % len(EnemyBullet.frames)

			center = self.rect.center
			self.image = EnemyBullet.frames[self.frame_index]
			self.rect = self.image.get_rect(center=center)

		if (
				self.rect.top > c.HEIGHT + 60
				or self.rect.bottom < -60
				or self.rect.right < -60
				or self.rect.left > c.WIDTH + 60
		):
			self.kill()