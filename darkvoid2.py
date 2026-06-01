import math
import pygame as pg
from game import Game
from pathlib import Path
import random


def _load_font(path, size, fallback=None):
    if Path(path).exists():
        return pg.font.Font(path, size)
    return pg.font.SysFont(fallback, size)

def alpha():

        pg.init()
        pg.mixer.init()

        clock = pg.time.Clock()
        home_dir = Path(__file__).parent.absolute()
        x_res = 1920
        y_res = 1080

        screen = pg.display.set_mode((x_res, y_res), pg.SRCALPHA, 32)
        pg.display.set_caption("Dark Void 2 - The Avoided")

        wallpaper = pg.image.load(
            home_dir / "assets" / "backgrounds" / "stimu_wallpaper.png"
        ).convert()
        wallpaper = pg.transform.smoothscale(wallpaper, (x_res, y_res))

        title_font = _load_font(
            home_dir / "assets" / "fonts" / "GoMonoNerdFontPropo-Bold.ttf",
            150,
            "arial black",
        )
        subtitle_font = _load_font(
            home_dir / "assets" / "fonts" / "GoMonoNerdFontPropo-Bold.ttf",
            72,
            "arial black",
        )
        prompt_font = _load_font(
            home_dir / "assets" / "fonts" / "VL-Gothic-Regular.ttf",
            42,
            "consolas",
        )

        icon_font = _load_font(
            home_dir / "assets" / "fonts" / "VL-Gothic-Regular.ttf",
            96,
            "consolas",
        )
        pg.display.set_icon(icon_font.render("DV2", True, (0, 255, 0)))

        try:
            pg.mixer.music.load(home_dir / "assets" / "audio" / "1000 Handz - Announcement.mp3")
            pg.mixer.music.play(-1)
            pg.mixer.music.set_volume(0.2)
        except pg.error:
            pass

        start_time = pg.time.get_ticks()
        wallpaper_duration = 5.0
        fade_duration = 1.2
        katakana_text = "ダーク ヴォイド 2"
        running = True

        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return False

                if event.type == pg.KEYDOWN:
                    elapsed = (pg.time.get_ticks() - start_time) / 1000

                    if event.key in (pg.K_SPACE, pg.K_RETURN) and elapsed > wallpaper_duration + fade_duration:
                        pg.mixer.music.fadeout(500)
                        return True

                    if event.key == pg.K_F1:
                        show_controls(screen, subtitle_font, prompt_font)

                    if event.key == pg.K_ESCAPE:
                        return False

            elapsed = (pg.time.get_ticks() - start_time) / 1000

            screen.blit(wallpaper, (0, 0))

            if elapsed < wallpaper_duration:
                pg.display.flip()
                clock.tick(60)
                continue

            fade_out = min(1, (elapsed - wallpaper_duration) / fade_duration)
            fade_in = min(1, max(0, elapsed - wallpaper_duration - fade_duration) / fade_duration)

            black = pg.Surface((x_res, y_res), pg.SRCALPHA)
            black.fill((0, 0, 0, int(255 * fade_out)))
            screen.blit(black, (0, 0))

            if fade_in <= 0:
                pg.display.flip()
                clock.tick(60)
                continue

            screen.fill((0, 0, 0))

            pulse = 175 + int(math.sin(elapsed * 2.4) * 50)
            title = title_font.render("DARK VOID 2", True, (pulse, 20, 30))
            title.set_alpha(int(255 * fade_in))
            title_rect = title.get_rect(center=(x_res // 2, y_res // 2 - 120))
            screen.blit(title, title_rect)

            subtitle = subtitle_font.render("THE AVOIDED", True, (255, 255, 255))
            subtitle.set_alpha(int(230 * fade_in))
            subtitle_rect = subtitle.get_rect(center=(x_res // 2, y_res // 2 + 24))
            screen.blit(subtitle, subtitle_rect)

            katakana = prompt_font.render(katakana_text, True, (120, 210, 255))
            katakana.set_alpha(int(210 * fade_in))
            katakana_rect = katakana.get_rect(center=(x_res // 2, y_res // 2 + 100))
            screen.blit(katakana, katakana_rect)

            for x, y, scale, phase in [
                (190, 170, 1.0, 0.0),
                (x_res - 190, y_res - 190, 0.9, 1.2),
                (260, y_res - 210, 0.75, 2.0),
                (x_res - 300, 180, 0.7, 2.8),
            ]:
                alpha = int((90 + math.sin(elapsed * 1.6 + phase) * 45) * fade_in)
                ghost = prompt_font.render(katakana_text, True, (60, 110, 170))
                ghost = pg.transform.smoothscale_by(ghost, scale)
                ghost.set_alpha(alpha)
                screen.blit(ghost, ghost.get_rect(center=(x, y)))

            if fade_in >= 1:
                prompt_alpha = 150 + int(math.sin(elapsed * 4.0) * 80)
                prompt = prompt_font.render("press SPACE to avoid or F1 for controls", True, (210, 230, 255))
                prompt.set_alpha(prompt_alpha)
                prompt_rect = prompt.get_rect(center=(x_res // 2, y_res - 120))
                screen.blit(prompt, prompt_rect)

            pg.display.flip()
            clock.tick(60)

        return False

def run_app():
    while True:
        if not alpha():
            break

        result = Game().run()

        if result != "restart":
            break

    pg.quit()
    pg.mixer.quit()


def show_controls(screen, bigfont, font):
    r = 255
    r_d = -1
    running = True
    clock = pg.time.Clock()

    def randomize():
        randomizer = random.choice(([r, random.choice([0, r, 255]), random.choice([r, random.choice([0, r, 255])]),
                             random.choice([r, random.choice([0, r, 255])])]))
        pat = (random.choice([(255, 0, randomizer), (255, 0, randomizer), (255, 0, randomizer)]))
        print(pat)
        return pat

    def colorize():
        text = []
        pattern = randomize()
        text.append(font.render("WASD or Arrows - Move the ship.", True, pattern))
        pattern = randomize()
        text.append(font.render("SPACE or Mouse button 1 - Fire main gun.", True, pattern))
        pattern = randomize()
        text.append(font.render("Mouse button 2 - Fire Vulcan cannon.", True, pattern))
        pattern = randomize()
        text.append(font.render("Left CTRL - Railgun if railgun powerup has been received.", True, pattern))
        pattern = randomize()
        text.append(font.render("Left ALT - Shield if shield powerup has been received.", True, pattern))
        pattern = randomize()
        text.append(font.render("Left SHIFT - Focus moving mode.", True, pattern))
        pattern = randomize()
        text.append(font.render("SPACE - Exit the controls screen.", True, pattern))
        pattern = randomize()
        text.append(font.render("ESC - Quit!", True, pattern))
        return text

    while running:
        text = colorize()
        screen.fill((0, 0, 0, 255))
        major_text = bigfont.render("Control instructions:", True, (255, 255, 255))

        screen.blit(major_text, (1920 // 2 - major_text.get_width() // 2, 200))
        for i, t in enumerate(text):
            screen.blit(t, (1920 // 2 - 500, 350 + i * 60))

        r += r_d
        if r < 1 or r > 254:
            r_d = -r_d
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pg.mixer.quit()
                    pg.quit()
                if event.key == pg.K_SPACE:
                    running = False

        dt = clock.tick(45) / 1000
        pg.display.flip()


if __name__ == "__main__":
    run_app()