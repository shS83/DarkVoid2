import random
import pygame as pg
import config as c

class FireEffect(pg.sprite.Sprite):
	def __init__(self, pos, size=(220, 160), pixel_size=3):
		super().__init__()

		self.pos = pg.Vector2(pos)

		self.buffer_width = size[0] // pixel_size
		self.buffer_height = size[1] // pixel_size
		self.pixel_size = pixel_size

		self.fire = [
            [0 for _ in range(self.buffer_width)]
			for _ in range(self.buffer_height)
		]

		self.palette = self.create_palette()

		#self.image = pg.Surface(size, pg.SRCALPHA)
		#self.rect = self.image.get_rect(center=self.pos)

	def create_palette(self):
		palette = []

		for i in range(64):
			palette.append((i * 4, 0, 0, i * 4))

		for i in range(64):
			palette.append((255, i * 3, 0, 255))

		for i in range(64):
			palette.append((255, 190 + i, i * 3, 255))

		for i in range(64):
			palette.append((255, 255, 190 + i, 255))

		return palette[:256]

	def update(self, dt):
		self.seed_bottom()
		self.propagate_fire()
		self.render_fire()

	def seed_bottom(self):
		bottom = self.buffer_height - 1

		for x in range(self.buffer_width):
			self.fire[bottom][x] = random.randint(180, 255)

		# occasional hotter bursts
		for _ in range(6):
			x = random.randint(0, self.buffer_width - 1)
			self.fire[bottom][x] = 255

	def propagate_fire(self):
		for y in range(self.buffer_height - 2, 0, -1):
			for x in range(1, self.buffer_width - 1):

				samples = [
					self.fire[y + 1][x - 1],
					self.fire[y + 1][x],
					self.fire[y + 1][x + 1],
				]

				if y + 2 < self.buffer_height:
					samples.append(self.fire[y + 2][x])

				value = sum(samples) // len(samples)

				cooling = random.randint(0, 3)
				value = max(0, value - cooling)

				drift = random.choice([-1, 0, 1])
				target_x = max(1, min(self.buffer_width - 2, x + drift))

				self.fire[y][target_x] = value

	def render_fire(self):
		c.screen.fill((0, 0, 0, 0))

		for y in range(self.buffer_height):
			for x in range(self.buffer_width):
				value = self.fire[y][x]

				if value <= 0:
					continue

				color = self.palette[value]

				rect = (
                    x * self.pixel_size,
                    y * self.pixel_size,
                    self.pixel_size,
                    self.pixel_size,
                )

				pg.draw.rect(c.screen, color, rect)

fire = FireEffect(
	pos=(c.WIDTH + 1280 // 2, c.HEIGHT+768 // 2),
	size=(640,480),
	pixel_size=2
)
				# self.effects.add(fire)
				# self.all_sprites.add(fire)
running=True
clock = pg.Clock()

while running:
	dt = clock.tick(60) / 1000
	for event in pg.event.get():
		if event.type == pg.QUIT:
			running = False
		if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
			running = False
	FireEffect.update(fire, dt)
	pg.display.flip()
