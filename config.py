import pygame as pg
import os
from entities.events import Event
from pathlib import Path

pg.init()
pg.mixer.init()
pg.mixer.music.set_volume(0.2)
HOME_DIR = os.path.dirname(__file__)

x_res = 1920
y_res = 1080
screen = pg.display.set_mode((x_res, y_res), pg.SRCALPHA, 32)
FPS = 60
DEBUG = False
OVERLAY_TIMER = 5000
BOSS_SPAWN_DELAY = 30
PLAYER_SPEED = 500
PLAYER_FOCUS_SPEED = 180
PLAYER_FIRE_COOLDOWN = 0.08
ENEMY_BULLET_SPEED = 180
ENEMY_BULLET_COOLDOWN = 0.01
ENEMY_HP = 5
PLAYER_BULLET_SPEED = 400
PLAYER_HITBOX_RADIUS = 4

BOSS1 = pg.image.load(
    Path(f"{HOME_DIR}", "assets", "ships", "bosses", "dark-crusader.png")
).convert_alpha()
BOSS2 = pg.image.load(
    Path(f"{HOME_DIR}", "assets", "ships", "bosses", "boss-2.png")
).convert_alpha()
BOSS3 = pg.image.load(
    Path(f"{HOME_DIR}", "assets", "ships", "bosses", "foobarhead1.png")
).convert_alpha()
ROCK1 = pg.image.load(
    Path(f"{HOME_DIR}", "assets", "rocks", "rock_1.png")
).convert_alpha()
ROCK2 = pg.image.load(
    Path(f"{HOME_DIR}", "assets", "rocks", "rock_2.png")
).convert_alpha()
ROCK3 = pg.image.load(
    Path(f"{HOME_DIR}", "assets", "rocks", "rock_3.png")
).convert_alpha()
ROCK4 = pg.image.load(
    Path(f"{HOME_DIR}", "assets", "rocks", "rock_4.png")
).convert_alpha()
ROCK5 = pg.image.load(
    Path(f"{HOME_DIR}", "assets", "rocks", "rock_5.png")
).convert_alpha()
ROCK6 = pg.image.load(
    Path(f"{HOME_DIR}", "assets", "rocks", "rock_6.png")
).convert_alpha()
BEACH1 = pg.image.load(
    Path(f"{HOME_DIR}", "assets", "backgrounds", "misc", "beach_1.jpg")
).convert()
BEACH2 = pg.image.load(
    Path(f"{HOME_DIR}", "assets", "backgrounds", "misc", "beach_2.jpg")
).convert()
BEACH3 = pg.image.load(
    Path(f"{HOME_DIR}", "assets", "backgrounds", "misc", "beach_3.jpg")
).convert()
BEACH4 = pg.image.load(
    Path(f"{HOME_DIR}", "assets", "backgrounds", "misc", "beach_4.jpg")
).convert()
PALLO1 = pg.transform.scale(
    pg.image.load(
        Path(f"{HOME_DIR}", "assets", "balls", "metallipallo_1.png")
    ).convert_alpha(),
    (64, 64),
)
PALLO2 = pg.transform.scale(
    pg.image.load(
        Path(f"{HOME_DIR}", "assets", "balls", "metallipallo_2.png")
    ).convert_alpha(),
    (64, 64),
)
PALLO3 = pg.transform.scale(
    pg.image.load(
        Path(f"{HOME_DIR}", "assets", "balls", "metallipallo_3.png")
    ).convert_alpha(),
    (64, 64),
)
PALLO4 = pg.transform.scale(
    pg.image.load(
        Path(f"{HOME_DIR}", "assets", "balls", "metallipallo_4.png")
    ).convert_alpha(),
    (64, 64),
)
PALLO5 = pg.transform.scale(
    pg.image.load(
        Path(f"{HOME_DIR}", "assets", "balls", "metallipallo_5.png")
    ).convert_alpha(),
    (64, 64),
)
PALLOT = [PALLO1, PALLO2, PALLO3, PALLO4, PALLO5]
DING = pg.mixer.Sound(Path(f"{HOME_DIR}", "assets", "audio", "ding.mp3"))
BEACHES = [BEACH1, BEACH2, BEACH3, BEACH4]
BACKGROUND = BEACH3
ROCK_IMAGES = [ROCK1, ROCK2, ROCK3, ROCK4, ROCK5, ROCK6]
WIDTH = 1920
HEIGHT = 1080
BOSS_TIMER = 2000
# {"name": "Mr. Robot", "pos": (WIDTH // 2, -200), "lvl": 0, "boss_hp": 1, "boss_time": 500, "boss_image": pg.Surface((100,100))},
BOSS = [
    {
        "name": "Dark Crusader",
        "pos": (WIDTH // 2, -200),
        "lvl": 1,
        "boss_hp": 300,
        "boss_time": 3000,
        "boss_image": BOSS1,
    },
    {
        "name": "Eldritch Marauder",
        "pos": (WIDTH // 2, -400),
        "lvl": 2,
        "boss_hp": 400,
        "boss_time": 4000,
        "boss_image": BOSS2,
    },
    {
        "name": "Aural Alien",
        "lvl": 3,
        "pos": (WIDTH // 2, -300),
        "boss_hp": 500,
        "boss_time": 5000,
        "boss_image": BOSS3,
    },
]

BOSS4 = pg.image.load(
    Path(
        f"{HOME_DIR}",
        "assets",
        "ships",
        "bosses",
        "stage4_boss_void_dreadnought_full.png",
    )
).convert_alpha()

BOSS.append(
    {
        "name": "Void Dreadnought",
        "pos": (WIDTH // 2, -360),
        "lvl": 4,
        "boss_hp": 750,
        "boss_time": 6500,
        "boss_image": BOSS4,
    }
)

NEXTBOSS = False
SHIELD = False
BOSS_TIME = False
SCALE = 0.4
HOME_DIR = os.path.dirname(__file__)
MSG_FONT = pg.font.Font(
    Path(f"{HOME_DIR}", "assets", "fonts", "GoMonoNerdFontPropo-Bold.ttf", 60)
)
GOTHIC_FONT = pg.font.Font(
    Path(f"{HOME_DIR}", "assets", "fonts", "VL-Gothic-Regular.ttf", 36)
)
event = Event.DRUMROLL
