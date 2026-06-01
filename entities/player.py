import math
import pygame as pg
from pathlib import Path
import config as c
from entities.vulcan import VulcanBullet, MuzzleFlash, VulcanSpark, ShellCasing
from pygame import mixer
from entities.bullet import PlayerBullet
from entities.explosion import Explosion
from entities.particle import Particle
from entities.thruster_particle import ThrusterParticle
from entities.shield import Shield
from pygame.transform import rotate, smoothscale_by
import random
from entities.powerup import PowerUp
from entities import earth

class Player(pg.sprite.Sprite):
    def __init__(self, game, pos):
        super().__init__()
        pg.mixer.init()
        self.mixer = mixer
        self.bullet = None
        self.game = game
        self.shoot_mode = "normal"
        self.power_timer = 0
        self.lives = c.PLAYER_LIVES
        self.invincible_timer = 0
        self.thruster_timer = 0
        self.alive = True
        self.fire_timer = 0
        self.killed_by = None
        self.fire_cooldown = c.PLAYER_FIRE_COOLDOWN
        self.fire_cooldown2 = c.PLAYER_FIRE_COOLDOWN2
        self.fire_cooldown3 = c.PLAYER_FIRE_COOLDOWN3
        self.game = game
        self.pauseswitch = -1
        self.original_image = pg.image.load(
            Path(c.HOME_DIR, "assets", "ships", "finnfighter.png")
        ).convert_alpha()

        self.final_scale = c.PLAYER_SCALE
        self.intro_scale = c.PLAYER_INTRO_SCALE
        self.current_scale = self.intro_scale

        self.target_pos = pg.Vector2(pos[0], pos[1] - 150)
        self.spawn_pos = pg.Vector2(pos[0], c.HEIGHT + 220)
        self.pos = self.spawn_pos.copy()

        self.intro_active = True
        self.intro_done = False
        self.intro_phase = "rise"
        self.intro_timer = 0

        self.rebuild_visuals(self.current_scale, self.pos)
        self.image1 = pg.image.load(
            c.resource_path(Path(c.HOME_DIR, "assets", "ships", "Proper_warship.png"))
        ).convert_alpha()
        self.image2 = rotate(
            pg.image.load(
                c.resource_path(
                    Path(c.HOME_DIR, "assets", "ships", "lilac-thrusters.png")
                )
            ).convert_alpha(),
            180,
        )
        self.image3 = pg.image.load(
            c.resource_path(Path(c.HOME_DIR, "assets", "ships", "purplealus.png"))
        ).convert_alpha()
        self.image4 = pg.image.load(
            c.resource_path(Path(c.HOME_DIR, "assets", "ships", "turqoiseship.png"))
        ).convert_alpha()
        self.image5 = pg.image.load(
            c.resource_path(Path(c.HOME_DIR, "assets", "ships", "finnfighter.png"))
        ).convert_alpha()
        # self.images = [self.image5] #self.image1, self.image2, self.image3, self.image4]
        self.image = smoothscale_by(self.original_image, self.current_scale)
        # self.image = pg.transform.smoothscale_by(self.image, self.current_scale)
        self.rect = self.image.get_rect(center=pos)
        self.pos = pg.Vector2(self.rect.center)
        self.base_image = self.image.copy()
        self.flash_image = self.make_flash_image(self.base_image)
        self.flash_toggle_timer = 0
        self.speed = c.PLAYER_SPEED
        self.focus_speed = c.PLAYER_FOCUS_SPEED
        self.fire_cooldown = c.PLAYER_FIRE_COOLDOWN
        self.bullet_speed = c.PLAYER_BULLET_SPEED
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect.inflate(-96, -96)
        self.hitbox_radius = self.hitbox.width // 2
        self.hitbox_template = self.base_image.get_bounding_rect(min_alpha=24).inflate(
            -18, -18
        )
        c.PLAYER_HITBOX_RADIUS = self.hitbox_radius
        self.particles = pg.sprite.Group()
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.shield = False
        self.shield_active = False
        self.shield_hit_timer = 0
        self.shield_hit_cooldown = 0.06
        self.shield_image = pg.transform.scale(
            random.choice([c.PALLO1, c.PALLO2, c.PALLO3]), (160, 160)
        )
        self.shield_image_rect = self.shield_image.get_rect(center=pos)
        self.shield_amount = 0
        self.shield_sound = pg.mixer.Sound(
            Path(c.HOME_DIR, "assets", "audio", "ding.mp3")
        )
        self.shield_sound.set_volume(0.7)
        self.vulcan_timer = 0
        self.vulcan_heat = 0.0
        self.vulcan_heat_max = 3.0
        self.vulcan_overheated = False
        self.vulcan_heat_rate = 0.65
        self.vulcan_cool_rate = 0.35
        self.vulcan_recover_threshold = 0.25
        self.vulcan_cooldown = 0.05
        self.killer = "No-one"
        self.vulcan_side = -1
        self.vulcan_counter = 0
        self.vulcan_sound_timer = 0
        self.vulcan_sound_delay = 1
        self.minigun_sound = mixer.Sound(
            Path(c.HOME_DIR, "assets", "audio", "m61continued.ogg")
        )
        self.minigun_sound.set_volume(1.0)
        self.visible = True
        self.ending_active = False
        self.flash_timer = 0
        self.railgun_active = False
        self.railgun_timer = 0.0
        self.railgun_duration = 12.0
        self.default_fire_cooldown = self.fire_cooldown
        self.default_fire_cooldown2 = self.fire_cooldown2
        self.default_speed = c.PLAYER_SPEED
        self.super_speed = 700
        self.bullets_piercing = False

    def make_flash_image(self, image):
        flash = pg.Surface(image.get_size(), pg.SRCALPHA)

        # Copy only the alpha channel shape from original image
        alpha_mask = image.copy()
        alpha_mask.fill((255, 255, 255, 200), special_flags=pg.BLEND_RGBA_MULT)

        flash.blit(alpha_mask, (0, 0))
        flash.fill((255, 255, 255, 200), special_flags=pg.BLEND_RGB_MAX)

        return flash

    def ease_out_cubic(self, t):
        return 1 - pow(1 - t, 3)

    def rebuild_visuals(self, scale, center):
        width = max(1, int(self.original_image.get_width() * scale))
        height = max(1, int(self.original_image.get_height() * scale))

        self.base_image = pg.transform.smoothscale(self.original_image, (width, height))
        self.flash_image = self.make_flash_image(self.base_image)
        self.image = self.base_image
        self.rect = self.image.get_rect(center=center)

    def update_intro(self, dt):
        self.intro_timer += dt

        if self.intro_phase == "rise":
            t = min(1, self.intro_timer / c.PLAYER_INTRO_RISE_TIME)
            t = self.ease_out_cubic(t)

            self.pos = self.spawn_pos.lerp(self.target_pos, t)
            self.rect.center = self.pos

            if t >= 1:
                self.intro_phase = "scale_down"
                self.intro_timer = 0

        elif self.intro_phase == "scale_down":
            t = min(1, self.intro_timer / c.PLAYER_INTRO_SCALE_TIME)
            t = self.ease_out_cubic(t)

            self.current_scale = (
                self.intro_scale + (self.final_scale - self.intro_scale) * t
            )

            self.pos = self.target_pos.copy()
            self.rebuild_visuals(self.current_scale, self.pos)

            if t >= 1:
                self.current_scale = self.final_scale
                self.rebuild_visuals(self.current_scale, self.target_pos)

                self.pos = self.target_pos.copy()
                self.rect.center = self.pos

                self.intro_active = False
                self.intro_done = True
                self.hitbox = self.rect.inflate(-96, -96)
                self.hitbox_radius = self.hitbox.width // 2
                self.hitbox_template = self.base_image.get_bounding_rect(
                    min_alpha=24
                ).inflate(-18, -18)
                self.invincible_timer = max(self.invincible_timer, 1.2)

    def activate_shield(self):
        if self.shield_active:
            return False

        if self.shield_amount <= 0:
            return False

        self.shield_amount -= 1
        self.shield_active = True

        shield = Shield(self.game, self)

        self.game.effects.add(shield)
        self.game.all_sprites.add(shield)

        return True

    def shoot_railgun(self):
        self.image = pg.transform.scale(
            pg.image.load(c.resource_path(Path(c.HOME_DIR, "assets", "laser-red.png"))),
            size=(30, 120),
        )
        self.image2 = pg.transform.scale(
            pg.image.load(c.resource_path(Path(c.HOME_DIR, "assets", "laser-red.png"))),
            size=(30, 120),
        )
        self.image3 = pg.transform.scale(
            pg.image.load(c.resource_path(Path(c.HOME_DIR, "assets", "laser-red.png"))),
            size=(30, 120),
        )
        if self.image is not None:
            self.image.blit(
                self.image, (0, 0), special_flags=pg.BLEND_RGBA_MULT | pg.BLEND_ADD
            )
        if self.image2 is not None:
            self.image2.blit(
                self.image2, (0, 0), special_flags=pg.BLEND_RGBA_MULT | pg.BLEND_ADD
            )
        if self.image3 is not None:
            self.image3.blit(
                self.image3, (0, 0), special_flags=pg.BLEND_RGBA_MULT | pg.BLEND_ADD
            )
        self.bullet = PlayerBullet(
            self.game,
            self.rect.midtop,
            self.image,
            velocity=(0, -2000),
            piercing=self.bullets_piercing,
        )

        if self.fire_timer > 0:
            return
        if self.rect.y - self.bullet.rect.y < 0:
            self.bullet.kill()

        pg.mixer.Sound(Path(c.HOME_DIR, "assets", "audio", "lasercont.wav")).play()
        self.fire_timer = self.fire_cooldown
        self.game.player_bullets.add(self.bullet)
        self.game.all_sprites.add(self.bullet)

    def shoot_normal(self):
        bullet = PlayerBullet(
            self.game,
            self.rect.midtop,
            velocity=(0, -800),
            piercing=self.bullets_piercing,
        )
        if self.fire_timer > 0:
            return
        if self.rect.y - bullet.rect.y < 0:
            bullet.kill()
        pg.mixer.Sound(Path(c.HOME_DIR, "assets", "audio", "lasersound2.wav")).play()
        self.fire_timer = self.fire_cooldown2
        self.game.player_bullets.add(bullet)
        self.game.all_sprites.add(bullet)

    def shoot_spread(self):
        self.image = pg.Surface((6, 20), pg.SRCALPHA)
        # pg.draw.rect(self.image, (255, 0, 0), (0, 0, 5, 25))
        bullet_data = [
            ((self.rect.centerx, self.rect.top), (0, -850)),
            ((self.rect.centerx - 10, self.rect.top + 8), (-180, -760)),
            ((self.rect.centerx + 10, self.rect.top + 8), (180, -760)),
        ]
        if self.fire_timer > 0:
            return
        pg.mixer.Sound(Path(c.HOME_DIR, "assets", "audio", "lasersound.wav")).play()
        self.fire_timer = self.fire_cooldown
        for pos, velocity in bullet_data:
            if self.pos.y + 20 < 0:
                bullet.kill()
            bullet = PlayerBullet(
                self.game,
                pos,
                velocity=velocity,
                piercing=self.bullets_piercing,
            )
            self.game.player_bullets.add(bullet)
            self.game.all_sprites.add(bullet)

    def hit(self, killer=None):
        self.killer = killer
        if self.invincible_timer > 0 or not self.alive:
            return

        if self.shield_active:
            pg.mixer.Sound(Path(c.HOME_DIR, "assets", "audio", "ding.mp3")).play()
            return

        self.flash_timer = 0.05
        pg.mixer.Sound(Path(c.HOME_DIR, "assets", "audio", "clink.wav")).play()
        self.lives -= 1
        self.invincible_timer = 2.0

        for _ in range(100):
            particle = Particle(self.game, self.rect.center)
            self.game.effects.add(particle)
            self.game.all_sprites.add(particle)

        if self.lives <= 0:
            self.die(killer=killer)

    def die(self, killer):
        if not self.alive:
            return

        explosion_sound = f"{c.HOME_DIR}/assets/audio/explosion1-long.wav"
        pg.mixer.Sound(explosion_sound).play()
        explosion = Explosion(self.game, self.rect.center)
        self.game.effects.add(explosion)
        self.game.all_sprites.add(explosion)

        for _ in range(900):
            particle = Particle(self.game, self.rect.center)
            self.game.effects.add(particle)
            self.game.all_sprites.add(particle)

        self.alive = False
        self.game.game_over = True
        self.killer = killer
        self.kill()

    def apply_powerup(self, kind):
        if kind == "spread":
            self.reset_powerups()
            self.shoot_mode = "spread"
            self.power_timer = 12.0

        elif kind == "speed":
            self.speed = self.super_speed
            self.power_timer = 12.0

        elif kind == "laser":
            self.fire_cooldown2 = 0.001
            self.power_timer = 12.0

        elif kind == "cannon":
            self.reset_powerups()
            self.shoot_mode = "cannon"
            self.railgun_active = True
            self.railgun_timer = self.railgun_duration
            self.power_timer = self.railgun_duration
            self.fire_cooldown = 0.001

        elif kind == "piercing":
            self.bullets_piercing = True
            self.power_timer = 25.0

        elif kind == "health":
            self.lives += 3

        elif kind == "shield":
            self.shield = True
            self.shield_amount += self.game.level.player_shield_amount

    def shoot_vulcan(self, dt):
        self.vulcan_timer -= dt

        if self.vulcan_timer > 0:
            return

        if self.vulcan_overheated:
            return

        self.vulcan_timer = self.vulcan_cooldown
        self.vulcan_heat += dt
        self.vulcan_counter += 1
        # ic(f"Ammo spent: {self.vulcan_counter}")
        muzzle = self.get_vulcan_muzzle()
        direction = self.get_mouse_aim_direction(muzzle)

        # Tiny random spread makes it feel mechanical and violent.
        direction = direction.rotate(random.uniform(-3.5, 3.5))

        bullet_speed = 1450
        velocity = direction * bullet_speed

        tracer = self.vulcan_counter % 5 == 0

        bullet = VulcanBullet(
            self.game,
            muzzle,
            velocity,
            tracer=tracer,
            piercing=self.bullets_piercing,
        )

        self.game.player_bullets.add(bullet)
        self.game.all_sprites.add(bullet)

        self.spawn_vulcan_fx(muzzle, direction)
        self.play_vulcan_sound()

    def get_vulcan_muzzle(self):
        # Alternates between left and right barrel.
        self.vulcan_side *= -1

        x_offset = 9 * self.vulcan_side
        y_offset = -36

        return pg.Vector2(
            self.rect.centerx + x_offset,
            self.rect.centery + y_offset,
        )

    @staticmethod
    def get_mouse_aim_direction(muzzle):
        mx, my = pg.mouse.get_pos()
        target = pg.Vector2(mx, my)

        direction = target - muzzle

        if direction.length_squared() == 0:
            return pg.Vector2(0, -1)

        return direction.normalize()

    def spawn_vulcan_fx(self, muzzle, direction):
        flash = MuzzleFlash(self.game, muzzle, direction)
        self.game.effects.add(flash)
        self.game.all_sprites.add(flash)

        for _ in range(4):
            spark = VulcanSpark(self.game, muzzle, direction)
            self.game.effects.add(spark)
            self.game.all_sprites.add(spark)

        # Shell ejects sideways from the opposite side of the active barrel.
        shell_side = -self.vulcan_side

        if random.random() < 0.75:
            shell = ShellCasing(self.game, muzzle, shell_side)
            self.game.effects.add(shell)
            self.game.all_sprites.add(shell)

    def play_vulcan_sound(self):
        if self.vulcan_sound_timer > 0:
            return

        self.vulcan_sound_timer = self.vulcan_sound_delay

        if hasattr(self.game, "play_sound"):
            self.game.play_sound(self.minigun_sound, 0.11)
        else:
            self.minigun_sound.play()

    def receive_hit(self, killer=None):
        if self.invincible_timer > 0:
            return

        if self.shield_active:
            if self.shield_hit_timer <= 0:
                self.shield_hit_timer = self.shield_hit_cooldown

                if hasattr(self.game, "play_sound"):
                    self.game.play_sound(self.shield_sound, 0.5)
                else:
                    self.shield_sound.play()

            return

        self.hit(killer=killer)

    def update_vulcan_heat(self, dt, firing):
        if firing and not self.vulcan_overheated:
            self.vulcan_heat += self.vulcan_heat_rate * dt

            if self.vulcan_heat >= self.vulcan_heat_max:
                self.vulcan_heat = self.vulcan_heat_max
                self.vulcan_overheated = True

        else:
            self.vulcan_heat -= self.vulcan_cool_rate * dt

            if self.vulcan_heat < 0:
                self.vulcan_heat = 0

            if (
                self.vulcan_overheated
                and self.vulcan_heat <= self.vulcan_recover_threshold
            ):
                self.vulcan_overheated = False

    def reset_powerups(self):
        self.shoot_mode = "normal"
        self.railgun_active = False
        self.bullets_piercing = False
        self.speed = self.default_speed
        self.fire_cooldown = self.default_fire_cooldown
        self.fire_cooldown2 = self.default_fire_cooldown2

    def update_powerups(self, dt):
        if self.power_timer > 0:
            self.power_timer -= dt

            if self.power_timer <= 0:
                self.power_timer = 0
                self.reset_powerups()

        if self.railgun_timer > 0:
            self.railgun_timer -= dt

            if self.railgun_timer <= 0:
                self.railgun_timer = 0
                self.railgun_active = False

    def update(self, dt):
        if self.intro_active:
            self.update_intro(dt)
            return

        self.update_powerups(dt)

        if self.vulcan_heat >= self.vulcan_heat_max:
            self.vulcan_overheated = True

        if self.visible == True:
            keys = pg.key.get_pressed()
            mouse = pg.mouse.get_pressed()
            mx, my = pg.mouse.get_pos()
            direction = pg.Vector2(0, 0)
            self.fire_timer -= dt
            if keys[pg.K_LEFT] or keys[pg.K_a]:
                direction.x -= 1
            if keys[pg.K_RIGHT] or keys[pg.K_d]:
                direction.x += 1
            if keys[pg.K_UP] or keys[pg.K_w]:
                direction.y -= 1
            if keys[pg.K_DOWN] or keys[pg.K_s]:
                direction.y += 1
            if keys[pg.K_LCTRL] and self.railgun_active:
                self.shoot_railgun()
            if keys[pg.K_SPACE] or mouse[0] == 1:
                if self.shoot_mode == "spread":
                    self.shoot_spread()
                else:
                    self.shoot_normal()
            if keys[pg.K_LSHIFT]:
                self.speed = c.PLAYER_FOCUS_SPEED
            if not keys[pg.K_LSHIFT]:
                self.speed = self.default_speed
            firing_vulcan = mouse[2] or mouse[1]

            self.update_vulcan_heat(dt, firing_vulcan)

            if firing_vulcan and not self.vulcan_overheated:
                self.shoot_vulcan(dt)

                self.vulcan_timer -= dt
                self.vulcan_sound_timer -= dt
            if keys[pg.K_ESCAPE]:
                pg.quit()
        # For debugging
        if c.DEBUG:
            if keys[pg.K_F1]:
                self.game.level.stage = 4
                self.game.boss_time = True
                self.game.boss_timer = 0
            if keys[pg.K_F2]:
                ...
            if keys[pg.K_F3]:
                self.game.player.alive = False
                self.game.draw_game_over()
            if keys[pg.K_F4]:
                self.game.player.lives = 100
            if keys[pg.K_F5]:
                self.game.earth_updates = True
            if keys[pg.K_F6]:
                if self.game.boss:
                    self.game.boss.destroy()
            if keys[pg.K_F7]:
                self.game.victory = True
                self.game.end_game(victory=True)
            if keys[pg.K_F8]:
                ...
            if keys[pg.K_F9]:
                powerup = PowerUp(
                    self.game,
                    (random.randrange(0, 1920), 0),
                    kind=random.choice(
                        ["health", "speed", "spread", "laser", "cannon", "shield", "piercing"]
                    ),
                )
                self.game.powerups.add(powerup)
                self.game.all_sprites.add(powerup)
            if keys[pg.K_F11]:
                self.alive = False
            if keys[pg.K_F10]:
                c.BOSS_TIME = True

        self.thruster_timer -= dt

        if self.thruster_timer <= 0:
            self.thruster_timer = 0.008

            engine_left = (self.rect.centerx - 14, self.rect.centery + 45)
            engine_left2 = (self.rect.centerx - 34, self.rect.centery + 45)
            engine_right = (self.rect.centerx + 14, self.rect.centery + 45)
            engine_right2 = (self.rect.centerx + 34, self.rect.centery + 45)

            for engine_pos in [engine_left, engine_right, engine_left2, engine_right2]:
                # hot core
                for _ in range(8):
                    particle = ThrusterParticle(
                        self.game,
                        engine_pos,
                        direction=(0, 1),
                        color=(0, 0, 255),
                        speed_range=(480, 720),
                        size_range=(1, 4),
                        life_range=(0.12, 0.36),
                        spread=6,
                    )
                    self.game.effects.add(particle)
                    self.game.all_sprites.add(particle)

                # purple/blue outer flame
                for _ in range(8):
                    particle = ThrusterParticle(
                        self.game,
                        engine_pos,
                        direction=(0, 1),
                        color=(100, 180, 255),
                        speed_range=(180, 380),
                        size_range=(2, 6),
                        life_range=(0.18, 0.38),
                        spread=6,
                    )
                    self.game.effects.add(particle)
                    self.game.all_sprites.add(particle)

                # orange sparks
                if random.random() < 0.45:
                    particle = ThrusterParticle(
                        self.game,
                        engine_pos,
                        direction=(0, 1),
                        color=(255, 140, 140),
                        speed_range=(320, 700),
                        size_range=(2, 6),
                        life_range=(0.12, 0.42),
                        spread=15,
                    )
                    self.game.effects.add(particle)
                    self.game.all_sprites.add(particle)

        if self.shield_hit_timer > 0:
            self.shield_hit_timer -= dt

        if direction.length_squared() > 0:
            direction = direction.normalize()

        if self.invincible_timer > 0:
            self.flash_toggle_timer += dt
            self.invincible_timer -= dt

            if int(self.flash_toggle_timer * 12) % 2 == 0:
                self.image = self.flash_image
                self.image.set_alpha(255)
            else:
                self.image = self.base_image
                self.image.set_alpha(140)

        else:
            self.image = self.base_image
            self.image.set_alpha(255)
        self.rect.center = self.pos
        self.hitbox = self.hitbox_template.copy()
        self.hitbox.x += self.rect.x
        self.hitbox.y += self.rect.y
        self.pos += direction * self.speed * dt

        self.pos.x = max(32, min(c.WIDTH - 32, self.pos.x))
        self.pos.y = max(32, min(c.HEIGHT - 32, self.pos.y))

        self.rect.center = self.pos
