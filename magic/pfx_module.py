import pygame
import pygame.gfxdraw
import random
import math
import pygame.transform as tf
import config as c

x_res = 1920
y_res = 1080
NOW_MS = 0
timer = pygame.time.Clock()
pygame.init()
particles_group = pygame.sprite.Group()

class Particle(pygame.sprite.Sprite):
	global particles_group
	GRAVITY = -7.8

	def __init__(self, x, y, color, direction, tolerance, psizemax, opacitydelta, gravity):
		super(Particle, self).__init__()
		self.gravity = gravity
		self.x = x
		self.y = y
		self.color = color
		self.size = random.randint(1, psizemax)
		self.circle = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
		self.image = pygame.Surface((c.WIDTH, c.HEIGHT), pygame.SRCALPHA)
		pygame.gfxdraw.aacircle(self.circle, int(self.size / 2), int(self.size / 2), int(self.size / 2 - 1), self.color)
		pygame.gfxdraw.filled_circle(self.circle, int(self.size / 2), int(self.size / 2), int(self.size / 2 - 1),
		                             self.color)
		self.poly = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
		pygame.gfxdraw.aapolygon(self.poly, [(0, self.size), (self.size / 2, 0), (self.size, self.size)], self.color)
		pygame.gfxdraw.filled_polygon(self.poly, [(0, self.size), (self.size / 2, 0), (self.size, self.size)],
		                              self.color)
		self.surface = random.choice([self.poly, self.circle])
		self.surface = self.poly
		if self.color == (255, 255, 255):
			self.surface = self.circle
		if self.surface == self.circle:
			self.rotdelta = 0
			self.rotdeltach = 0
		else:
			self.rotdelta = random.randint(-360, 360)
			self.rotdeltach = random.randint(1, 10)
		self.image.blit(self.surface, (c.WIDTH // 2, c.HEIGHT // 2))
		self.opacity = 255
		self.opacitydelta = random.randint(5, 20) / 10 * opacitydelta
		# self.opacitydelta = opacitydelta
		self.opacitych = random.randint(2, 5)
		self.rect = self.image.get_rect()
		# self.ang = math.radians(random.randint(1, 360))
		self.ang = round(math.radians(random.randrange(direction - tolerance, direction + tolerance)))
		self.power = random.randint(1, 100)
		self.start_time = pygame.time.get_ticks()

	def collides_with_any(self, any):
		...

	def collides_with_tolerance(self, tolerance):
		...

	def update(self, screen):
		time_now = pygame.time.get_ticks()
		if (self.power > 0):
			time_change = (time_now - self.start_time)
			if (time_change > 0):
				time_change /= 200.0
				self.image = pygame.transform.rotate(self.surface, self.rotdelta)
				self.image.set_alpha(self.opacity)
				if self.rotdelta < 0:
					self.rotdelta -= self.rotdeltach
				else:
					self.rotdelta += self.rotdeltach
				if self.color == (255, 255, 255):
					self.opacity += self.opacitych
					if self.opacity < 1 or self.opacity > 255:
						self.opacitych = -self.opacitych
				else:
					self.opacity -= self.opacitydelta
				gravitydelta = self.GRAVITY * time_change * time_change / 2.0
				deltax = self.power * time_change * math.sin(self.ang)
				if self.gravity:
					deltay = self.power * time_change * math.cos(self.ang) + gravitydelta
				else:
					deltay = self.power * time_change * math.cos(self.ang)

				self.rect.center = (self.x + int(deltax), self.y - int(deltay))
				if self.opacity < 1:
					if self in particles_group:
						particles_group.remove(self)
					self.kill()

				if not screen.get_rect().colliderect(self.rect) or (
						self.gravity and self.rect.y > 0 and not screen.get_rect().colliderect(self.rect)):
					self.kill()

	def draw(self, screen):
		screen.fill((0, 0, 0))
		screen.blit(self.image, (0, 0))

	def move(self, screen):
		self.update(screen)


def add_stream(x, y, amount, color, direction, tolerance, psizemax, opacitydelta, gravity=True,
               secondcolor=(255, 255, 255)):
	for i in range(1, amount):
		if not i % 2:
			particles_group.add(Particle(x, y, secondcolor, direction, tolerance, psizemax, opacitydelta, gravity))
		else:
			particles_group.add(Particle(x, y, color, direction, tolerance, psizemax, opacitydelta, gravity))

running = True
add_stream(700, 700, 90, (255, 180, 0), 180, 10, 12, 0.6)

while running:
	for i in particles_group:
		i.update(c.screen)
		i.draw(c.screen)
	startTime = pygame.time.get_ticks()
