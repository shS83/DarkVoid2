import random
import pygame as pg
import config as c


class MapManager:
    def __init__(self, game):
        self.game = game
        self.scroll_speed = 120
        self.chunks = []

        self.ocean_images = [
            self.scale_to_screen_width(
                pg.image.load(f"{c.HOME_DIR}/assets/backgrounds/ocean/sea_chunk_1.png").convert()
            ),
            self.scale_to_screen_width(
                pg.image.load(f"{c.HOME_DIR}/assets/backgrounds/ocean/sea_chunk_2.png").convert()
            ),
            self.scale_to_screen_width(
                pg.image.load(f"{c.HOME_DIR}/assets/backgrounds/ocean/sea_chunk_3.png").convert()
            ),
        ]

        self.spawn_initial_chunks()

    def spawn_initial_chunks(self):
        y = 0

        while y > -c.HEIGHT * 2:
            image = random.choice(self.ocean_images)
            rect = image.get_rect(topleft=(0, y))
            self.chunks.append([image, rect])
            y -= rect.height

    def update(self, dt):
        for chunk in self.chunks:
            chunk[1].y += self.scroll_speed * dt

        self.chunks = [
            chunk for chunk in self.chunks
            if chunk[1].top < c.HEIGHT
        ]

        top_y = min(chunk[1].top for chunk in self.chunks)

        while top_y > -c.HEIGHT:
            image = random.choice(self.ocean_images)
            rect = image.get_rect(topleft=(0, top_y - image.get_height()))
            self.chunks.append([image, rect])
            top_y = rect.top

    def scale_to_screen_width(self, image, zoom=1.15):
        scale = (c.WIDTH * zoom) / image.get_width()
        new_width = int(image.get_width() * scale)
        new_height = int(image.get_height() * scale)

        return pg.transform.smoothscale(image, (new_width, new_height))

    def draw(self, screen):
        for image, rect in self.chunks:
            x = (c.WIDTH - image.get_width()) // 2
            screen.blit(image, (x, rect.y))