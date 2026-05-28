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
	def __init__(self, game, pos, velocity, color=[255, 255, 255, 20]):
		super().__init__()
		self.color = [0, 0, 0, 0.0]
		self.colors = {"RED": [255, 0, 0, 255],
                       "GREEN": [0, 255, 0, 255],
                       "BLUE": [0, 0, 255, 255],
                       "WHITE": [255, 255, 255, 255],
                       "BLACK": [0, 0, 0, 255],
                       "YELLOW": [255, 255, 0, 255],
                       "MAGENTA": [255, 0, 255, 255],
                       "CYAN": [0, 255, 255, 255],
                       "ORANGE": [255, 115, 0, 255],
                       "LIME": [128, 255, 0, 255],
                       "PEACH": [255, 200, 128, 255],
                       "PURPLE": [128, 0, 128, 255],
                       "PINK": [255, 128, 255, 255],
                       }
		self.color = random.choice([color, random.choice(list(self.colors.values()))])
		self.game = game
		self.pos = pg.Vector2(pos)
		self.velocity = pg.Vector2(velocity)
		self.offset = [0, 0, 0, 0.0]
		self.radius = 6

		self.image = self.make_glow_bullet()
		self.rect = self.image.get_rect(center=self.pos)

	def check_abs(self, color: tuple[int, int, int, int], offset: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
		if self.color[0] == 255:
			red = 255
		else:
			red = abs(255-self.color[0]-self.offset[0])
		if self.color[1] == 255:
			green = 255
		else:
			green = abs(self.color[1] - self.offset[1])
		if self.color[2] == 255:
			blue = 255
		else:
			blue = abs(self.color[2] - self.offset[2])
		if self.color[3] == 255:
			alpha = 255
		else:
			alpha = self.color[3]

		return red, green, blue, alpha

	def make_glow_bullet(self):
		size = 42
		center = size // 2

		image = pg.Surface((size, size), pg.SRCALPHA)

		# Soft outer glow
		self.offset = (0, 75, 235, 230)
		self.color = self.check_abs(self.color, self.offset)

		pg.draw.circle(image, self.color, (center, center), 20)

		self.offset = (0, 55, 215, 210)
		self.color = self.check_abs(self.color, self.offset)
		pg.draw.circle(image, self.color, (center, center), 15)

		self.offset = (0, 15, 175, 175)
		self.color = self.check_abs(self.color, self.offset)
		pg.draw.circle(image, self.color, (center, center), 11)

		# Yellowish ring
		self.offset = (0, 10, 55, 65)
		self.color = self.check_abs(self.color, self.offset)

		red_off = abs(self.offset[0]-self.color[0])
		green_off = abs(self.offset[1]-self.color[1]-10)
		blue_off = abs(self.offset[2]-self.color[2]-55)
		alpha_off = abs(self.offset[3]-65)
		ic(red_off, green_off, blue_off, alpha_off)
		ic(self.color)
		pg.draw.circle(image, (red_off, green_off, blue_off, alpha_off), (center, center), 8, width=2)

		self.offset = (0, 70, 70)
		self.color = self.check_abs(self.color, self.offset)
		# Hot core
		ic(red_off, green_off, blue_off, 255)
		ic(self.color)
		pg.draw.circle(image, (abs(self.color[0]-red_off), abs(self.color[1]-green_off), abs(self.color[2]-blue_off), 255), (center, center), 5)
		
		self.offset = (0, 10, 35, 65)
		self.color = self.check_abs(self.color, self.offset)
		ic(red_off, green_off, blue_off, self.offset[3]-65)
		ic(self.color)
		pg.draw.circle(image, (abs(self.color[0]-red_off), abs(self.color[1]-green_off), abs(self.color[2]-blue_off), 255), (center, center), 2)

		return image

	def update(self, dt):
		self.pos += self.velocity * dt
		self.rect.center = self.pos

		if (
			self.rect.top > c.HEIGHT + 50
			or self.rect.bottom < -50
			or self.rect.right < -50
			or self.rect.left > c.WIDTH + 50
		):
			self.kill()


	def update(self, dt):
		self.pos += self.velocity * dt
		self.rect.center = self.pos

		if (
				self.rect.top > c.HEIGHT
				or self.rect.bottom < 0
				or self.rect.right < 0
				or self.rect.left > c.WIDTH
		):
			self.kill()
