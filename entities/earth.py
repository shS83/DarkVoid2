import config as c
from pygame import Vector2
from core.spritegroups import all_sprites

class Earth:
    def __init__(self, x: int = c.WIDTH // 2, y = -300):
        self.image = c.EARTH
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.target_y = c.HEIGHT // 2

    def update(self):
        if self.rect.y < self.target_y:
            self.rect.y += 1
