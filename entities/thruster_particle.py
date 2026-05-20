import random
import pygame as pg


class ThrusterParticle(pg.sprite.Sprite):
	def __init__(
			self,
			game,
			pos,
			direction,
			color=(80, 200, 255),
			speed_range=(80, 180),
			size_range=(2, 5),
			life_range=(0.15, 0.35),
			spread=25,
	):
		super().__init__()

		self.game = game
		self.pos = pg.Vector2(pos)

		base_direction = pg.Vector2(direction)

		if base_direction.length_squared() == 0:
			base_direction = pg.Vector2(0, 1)

		base_direction = base_direction.normalize()

		final_direction = base_direction.rotate(
			random.uniform(-spread, spread)
		)

		self.velocity = final_direction * random.uniform(*speed_range)

		self.life = random.uniform(*life_range)
		self.max_life = self.life

		self.size = random.randint(*size_range)
		self.color = color

		self.image = pg.Surface((self.size, self.size), pg.SRCALPHA)
		pg.draw.circle(
			self.image,
			self.color,
			(self.size // 2, self.size // 2),
			self.size // 2
		)

		self.rect = self.image.get_rect(center=self.pos)

	def update(self, dt):
		self.life -= dt

		if self.life <= 0:
			self.kill()
			return

		self.pos += self.velocity * dt
		self.velocity *= 0.93

		self.rect.center = self.pos

		alpha = int(255 * (self.life / self.max_life))
		self.image.set_alpha(alpha)
