import math
import random
import pygame as pg
import pygame.gfxdraw
from pygame.locals import *


class Particle(pygame.sprite.Sprite):

    def __init__(self, x, y, power, size, color=(255, 255, 255), lift=13):
        super().__init__()
        self.x = x
        self.y = y
        self.size = 5 + size
        self.lift = lift
        self.ang = math.radians(random.randint(1, 360))
        self.power = 1 + power + random.randint(1, 10)
        self.poly = pg.Surface((self.size, self.size), SRCALPHA)
        self.surface = pg.Surface((self.size, self.size), SRCALPHA)

        if color == (255, 255, 255):
            rc = 200 + random.randint(1, 55)
            self.color = (rc, rc, rc)
            pg.gfxdraw.filled_circle(self.surface, int(self.size / 2), int(self.size / 2), int(self.size / 2 - 1),
                                     self.color)
        else:
            self.color = color
            pygame.gfxdraw.filled_polygon(self.poly, [(0, self.size), (self.size / 2, 0), (self.size, self.size)],
                                          self.color)
            self.surface = self.poly

        if self.surface == self.poly:
            self.rotdelta = random.randint(-360, 360)
            self.rotdeltach = random.randint(1, 10)
        else:
            self.rotdelta = 0
            self.rotdeltach = 0

        self.image = self.surface
        self.rect = self.image.get_rect()
        self.opacity = 255
        self.opacitydelta = random.randint(5, 20) / 5
        self.start_time = pygame.time.get_ticks()

    def update(self, screen):

        time_now = pygame.time.get_ticks()
        if self.power > 0:
            time_change = (time_now - self.start_time)
            if time_change > 0:
                time_change /= 200.0
                if self.size > 0:
                    scaled = pygame.transform.smoothscale(self.surface, (self.size * 1.5, self.size * 1.5))
                    self.image = pygame.transform.rotate(scaled, self.rotdelta)
                self.image.set_alpha(self.opacity)
                if self.rotdelta < 0:
                    self.rotdelta -= self.rotdeltach
                else:
                    self.rotdelta += self.rotdeltach
                liftdelta = self.lift * time_change * time_change / 2.0
                deltax = self.power * time_change * math.sin(self.ang)
                if self.lift is not False:
                    deltay = self.power * time_change * math.cos(self.ang) + liftdelta
                else:
                    deltay = self.power * time_change * math.cos(self.ang)

                self.rect.center = (self.x + int(deltax), self.y - int(deltay))
                self.size -= 0.1
                self.opacity -= self.opacitydelta

                if self.opacity < 1 or self.size < 1:
                    self.kill()

                if not screen.get_rect().colliderect(self.rect) or (self.lift is not False and self.rect.y < 0 and not
                                                                    screen.get_rect().colliderect(self.rect)):
                    self.kill()


def add_smoke(x, y, amount, color=(255, 255, 255), power=15, size=10, lift=13):
    for i in range(1, amount):
        if not i % 10:
            particles.append(Particle(x, y, power, size, color, lift=False))
        else:
            particles.append(Particle(x, y, power, size, (255, 255, 255), lift))
    spriteGroup.add(particles)


particles = []
spriteGroup = pygame.sprite.Group()
