import math
import random
import pygame as pg
import config as c


class VulcanBullet(pg.sprite.Sprite):
    def __init__(self, game, pos, velocity, tracer=False):
        super().__init__()

        self.game = game
        self.pos = pg.Vector2(pos)
        self.velocity = pg.Vector2(velocity)
        self.damage = 1
        self.tracer = tracer

        if tracer:
            self.image = pg.Surface((5, 24), pg.SRCALPHA)
            pg.draw.rect(self.image, (255, 240, 120), (0, 0, 5, 24))
            pg.draw.rect(self.image, (255, 120, 20), (1, 0, 3, 24))
        else:
            self.image = pg.Surface((3, 14), pg.SRCALPHA)
            pg.draw.rect(self.image, (255, 230, 170), (0, 0, 3, 14))

        direction = self.velocity.normalize()

        # Image is originally drawn pointing upward.
        angle = -math.degrees(math.atan2(direction.y, direction.x)) - 90
        self.image = pg.transform.rotate(self.image, angle)

        self.rect = self.image.get_rect(center=self.pos)

    def update(self, dt):
        self.pos += self.velocity * dt
        self.rect.center = self.pos

        if (
            self.rect.bottom < -40
            or self.rect.top > c.HEIGHT + 40
            or self.rect.right < -40
            or self.rect.left > c.WIDTH + 40
        ):
            self.kill()


class MuzzleFlash(pg.sprite.Sprite):
    def __init__(self, game, pos, direction):
        super().__init__()

        self.game = game
        self.pos = pg.Vector2(pos)
        self.direction = pg.Vector2(direction)

        self.life = 0.055
        self.max_life = self.life

        self.image = pg.Surface((34, 34), pg.SRCALPHA)
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, dt):
        self.life -= dt

        if self.life <= 0:
            self.kill()
            return

        self.image.fill((0, 0, 0, 0))

        alpha = int(255 * (self.life / self.max_life))
        center = (17, 17)

        pg.draw.circle(self.image, (255, 240, 160, alpha), center, 9)
        pg.draw.circle(self.image, (255, 120, 30, alpha), center, 15, width=2)

        self.rect.center = self.pos


class VulcanSpark(pg.sprite.Sprite):
    def __init__(self, game, pos, direction):
        super().__init__()

        self.game = game
        self.pos = pg.Vector2(pos)

        base = pg.Vector2(direction)
        if base.length_squared() == 0:
            base = pg.Vector2(0, -1)
        else:
            base = base.normalize()

        self.velocity = base.rotate(random.uniform(-35, 35)) * random.uniform(90, 260)

        self.life = random.uniform(0.05, 0.15)
        self.max_life = self.life

        self.size = random.randint(2, 4)
        self.image = pg.Surface((self.size, self.size), pg.SRCALPHA)

        pg.draw.circle(
            self.image,
            (255, random.randint(150, 230), 40),
            (self.size // 2, self.size // 2),
            max(1, self.size // 2),
        )

        self.rect = self.image.get_rect(center=self.pos)

    def update(self, dt):
        self.life -= dt

        if self.life <= 0:
            self.kill()
            return

        self.pos += self.velocity * dt
        self.velocity *= 0.88
        self.rect.center = self.pos

        alpha = int(255 * (self.life / self.max_life))
        self.image.set_alpha(alpha)


class ShellCasing(pg.sprite.Sprite):
    def __init__(self, game, pos, side):
        super().__init__()

        self.game = game
        self.pos = pg.Vector2(pos)

        x_speed = random.uniform(80, 180) * side
        y_speed = random.uniform(40, 120)

        self.velocity = pg.Vector2(x_speed, y_speed)
        self.gravity = pg.Vector2(0, 420)

        self.life = random.uniform(0.25, 0.45)
        self.max_life = self.life

        self.image = pg.Surface((5, 2), pg.SRCALPHA)
        pg.draw.rect(self.image, (210, 160, 70), (0, 0, 5, 2))

        self.rect = self.image.get_rect(center=self.pos)

    def update(self, dt):
        self.life -= dt

        if self.life <= 0:
            self.kill()
            return

        self.velocity += self.gravity * dt
        self.pos += self.velocity * dt
        self.rect.center = self.pos

        alpha = int(255 * (self.life / self.max_life))
        self.image.set_alpha(alpha)