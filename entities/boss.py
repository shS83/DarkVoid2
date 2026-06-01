import random
import pygame as pg
from entities.events import Event
from entities.particle import Particle
from entities.thruster_particle import ThrusterParticle
from entities.explosion import Explosion
from entities.bullet import EnemyBullet
import config as c
from pathlib import Path


class Boss(pg.sprite.Sprite):
    def __init__(
        self,
        game,
        name="Unnamed",
        pos=(320, -160),
        image=None,
        hp=1000,
        lvl=1,
    ):
        super().__init__()

        self.game = game
        self.name = name
        self.lvl = lvl
        self.hp = hp
        self.max_hp = hp

        if image is None:
            image = pg.image.load(
                f"{c.HOME_DIR}/assets/ships/bosses/foobarhead1.png"
            ).convert_alpha()

        elif isinstance(image, (str, Path)):
            image = pg.image.load(image).convert_alpha()
        if self.name == "Dark Crusader":
            self.image = pg.transform.rotate(
                pg.transform.smoothscale(image, (800, 800)), 180
            )
        else:
            self.image = pg.transform.rotate(
                pg.transform.smoothscale(image, (800, 800)), 0
            )
        self.base_image = self.image.copy()
        self.mask = pg.mask.from_surface(self.base_image)
        self.hitbox_template = self.base_image.get_bounding_rect(min_alpha=24).inflate(
            -18, -18
        )
        self.flash_image = self.make_flash_image(self.base_image)
        self.flash_timer = 0

        self.rect = self.image.get_rect(center=pos)
        self.pos = pg.Vector2(self.rect.center)

        self.hitbox = self.hitbox_template.copy()
        self.hitbox.x += self.rect.x
        self.hitbox.y += self.rect.y

        self.target_y = 250
        self.speed = 120
        self.entering = True

        self.shoot_timer = 0.8
        self.shoot_delay = 0.8
        self.secondary_timer = 1.2

        self.phase_index = 0
        self.phase_timer = 0

        self.thruster_timer = 0.12

        self.phases = [
            self.phase_intro,
            self.phase_radial,
            self.phase_spiral,
            self.phase_maze,
            self.phase_desperation,
        ]

    def update(self, dt):
        if self.pos.y < self.target_y:
            self.entering = True
            self.pos.y += self.speed * dt

            if self.pos.y > self.target_y:
                self.pos.y = self.target_y
        else:
            self.entering = False

        self.rect.center = self.pos
        self.hitbox = self.hitbox_template.copy()
        self.hitbox.x += self.rect.x
        self.hitbox.y += self.rect.y

        self.shoot_timer -= dt
        self.secondary_timer -= dt
        self.phase_timer += dt

        self.phases[self.phase_index](dt)

        self.thruster_timer -= dt
        if self.thruster_timer <= 0:
            self.thruster_timer = 0.04
            particle = ThrusterParticle(
                self.game, self.rect.midtop, direction=(0, -1), color=(255, 120, 40)
            )
            self.game.effects.add(particle)
            self.game.all_sprites.add(particle)

        if self.flash_timer > 0:
            self.flash_timer -= dt
            self.image = self.flash_image
        else:
            self.image = self.base_image

    def next_phase(self):
        self.phase_timer = 0
        self.shoot_timer = 0.4
        self.secondary_timer = 1.0

        if self.phase_index < len(self.phases) - 1:
            self.phase_index += 1
        else:
            self.phase_index = len(self.phases) - 1

    def fire_bullet(self, pos, velocity):
        bullet = EnemyBullet(self.game, pos, velocity, owner=self.name)
        self.game.enemy_bullets.add(bullet)
        self.game.all_sprites.add(bullet)

    def rank(self):
        return max(1, min(4, int(self.lvl)))

    def player_direction(self, pos=None):
        if pos is None:
            pos = self.pos

        direction = self.game.player.pos - pg.Vector2(pos)

        if direction.length_squared() == 0:
            return pg.Vector2(0, 1)

        return direction.normalize()

    def aimed_shot(self, speed=260):
        self.fire_bullet(self.rect.center, self.player_direction() * speed)

    def aimed_spread(self, count=7, speed=260, spread=50):
        direction = self.player_direction()

        start = -spread / 2
        step = spread / max(1, count - 1)

        for i in range(count):
            angle = start + step * i
            self.fire_bullet(self.rect.center, direction.rotate(angle) * speed)

    def radial_burst(self, count=32, speed=190, offset=0):
        for i in range(int(count)):
            angle = offset + 360 * i / count
            direction = pg.Vector2(1, 0).rotate(angle)
            self.fire_bullet(self.rect.center, direction * speed)

    def spiral_burst(self, arms=4, speed=220, spin=180):
        base_angle = self.phase_timer * spin

        for i in range(int(arms)):
            angle = base_angle + i * (360 / arms)
            direction = pg.Vector2(1, 0).rotate(angle)
            self.fire_bullet(self.rect.center, direction * speed)

    def lane_wall(self, columns=18, speed=180, gap_index=None, gap_width=2):
        if gap_index is None:
            gap_index = columns // 2

        y = self.rect.centery + 120
        step = c.WIDTH / (columns + 1)

        for i in range(columns):
            if abs(i - gap_index) <= gap_width:
                continue

            x = step * (i + 1)
            wobble = pg.Vector2(random.uniform(-18, 18), speed)
            self.fire_bullet((x, y), wobble)

    def side_pincer(self, rows=8, speed=190):
        for i in range(rows):
            y = 160 + i * 90
            down_bias = 90 + i * 8
            self.fire_bullet((-16, y), pg.Vector2(speed, down_bias))
            self.fire_bullet((c.WIDTH + 16, y + 45), pg.Vector2(-speed, down_bias))

    def phase_intro(self, dt):
        if self.phase_timer > 2.5:
            self.next_phase()

    def phase_radial(self, dt):
        rank = self.rank()
        self.shoot_delay = max(0.48, 0.95 - rank * 0.08)

        if self.shoot_timer <= 0:
            self.shoot_timer = self.shoot_delay
            self.radial_burst(
                count=14 + rank * 5,
                speed=145 + rank * 35,
                offset=self.phase_timer * (28 + rank * 8),
            )

        if self.secondary_timer <= 0:
            self.secondary_timer = 1.35
            self.aimed_spread(
                count=3 + rank * 2,
                speed=170 + rank * 32,
                spread=28 + rank * 8,
            )

        if self.phase_timer > 9:
            self.next_phase()

    def phase_spiral(self, dt):
        rank = self.rank()
        self.shoot_delay = max(0.18, 0.42 - rank * 0.045)

        if self.shoot_timer <= 0:
            self.shoot_timer = self.shoot_delay
            self.spiral_burst(
                arms=2 + rank,
                speed=145 + rank * 28,
                spin=90 + rank * 24,
            )

        if self.secondary_timer <= 0:
            self.secondary_timer = 1.1
            self.aimed_spread(
                count=5 + rank,
                speed=170 + rank * 25,
                spread=24 + rank * 7,
            )

        if self.phase_timer > 10:
            self.next_phase()

    def phase_maze(self, dt):
        rank = self.rank()
        self.shoot_delay = max(0.5, 1.0 - rank * 0.08)

        if self.shoot_timer <= 0:
            self.shoot_timer = self.shoot_delay
            columns = 12 + rank * 4
            gap_travel = (pg.math.Vector2(1, 0).rotate(self.phase_timer * 70).x + 1) / 2
            gap_index = round(gap_travel * (columns - 1))
            gap_width = 2 if rank < 4 else 1
            self.lane_wall(
                columns=columns,
                speed=135 + rank * 30,
                gap_index=gap_index,
                gap_width=gap_width,
            )

        if self.secondary_timer <= 0:
            self.secondary_timer = max(0.75, 1.25 - rank * 0.08)
            self.aimed_spread(
                count=5 + rank * 2,
                speed=185 + rank * 28,
                spread=34 + rank * 8,
            )

            if rank >= 3:
                self.side_pincer(rows=4 + rank, speed=145 + rank * 22)

        if self.phase_timer > 11:
            self.next_phase()

    def phase_desperation(self, dt):
        rank = self.rank()
        self.shoot_delay = max(0.28, 0.68 - rank * 0.08)

        if self.shoot_timer <= 0:
            self.shoot_timer = self.shoot_delay
            self.radial_burst(
                count=16 + rank * 6,
                speed=170 + rank * 38,
                offset=self.phase_timer * (65 + rank * 18),
            )
            self.spiral_burst(
                arms=3 + rank,
                speed=145 + rank * 34,
                spin=150 + rank * 22,
            )

        if self.secondary_timer <= 0:
            self.secondary_timer = max(0.65, 1.1 - rank * 0.08)
            self.aimed_spread(
                count=7 + rank * 2,
                speed=210 + rank * 32,
                spread=48 + rank * 10,
            )

            if rank >= 4:
                columns = 24
                gap_index = int((self.phase_timer * 3) % columns)
                self.lane_wall(
                    columns=columns,
                    speed=250,
                    gap_index=gap_index,
                    gap_width=1,
                )

    def make_flash_image(self, image):
        flash = pg.Surface(image.get_size(), pg.SRCALPHA)

        # Copy only the alpha channel shape from original image
        alpha_mask = image.copy()
        alpha_mask.fill((255, 255, 255, 200), special_flags=pg.BLEND_RGBA_MULT)

        flash.blit(alpha_mask, (0, 0))
        flash.fill((255, 255, 255, 200), special_flags=pg.BLEND_RGB_MAX)

        return flash

    def shoot(self):
        self.shoot_delay = 1.5
        self.shoot_timer = self.shoot_delay

        direction = self.game.player.pos - self.pos

        if direction.length_squared() == 0:
            direction = self.game.player.pos - self.pos
        else:
            direction = direction.normalize()

        bullet = EnemyBullet(self.game, self.rect.center, direction)

        self.game.enemy_bullets.add(bullet)
        self.game.all_sprites.add(bullet)

    def damage(self, amount):
        if self.entering:
            return

        self.hp -= amount
        self.flash_timer = 0.005

        if self.hp <= 0:
            self.destroy()

    def destroy(self):
        explosion = Explosion(self.game, self.rect.center, boss=True)
        self.game.effects.add(explosion)
        self.game.all_sprites.add(explosion)

        for _ in range(250):
            particle = Particle(self.game, self.rect.center)
            self.game.effects.add(particle)
            self.game.all_sprites.add(particle)

        self.game.score += 5000

        c.BOSS_TIME = False
        c.event = c.Event.NEXTLEVEL

        self.game.boss = None
        self.game.level_timer = 0
        self.game.boss_spawned_this_level = False

        final_boss_dead = (
            self.lvl >= c.FINAL_BOSS_LEVEL or self.name == c.FINAL_BOSS_NAME
        )

        self.kill()

        if final_boss_dead:
            self.game.start_world_transition()
        else:
            self.game.level.up()
