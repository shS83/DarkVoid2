import math
import pygame as pg
from game import Game
from pathlib import Path
from ui.rainbow_text import RainbowText


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
                        if not show_controls(screen, subtitle_font, prompt_font):
                            return False

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
    if alpha():
        while True:
            result = Game().run()
            if result != "restart":
                break

    pg.quit()
    pg.mixer.quit()


def show_controls(screen, bigfont, font):
    clock = pg.time.Clock()
    lines = [
        "WASD or Arrows - Move the ship.",
        "SPACE or Mouse button 1 - Fire main gun.",
        "Mouse button 2 - Fire Vulcan cannon.",
        "Left CTRL - Railgun if railgun powerup has been received.",
        "Left ALT - Shield if shield powerup has been received.",
        "Left SHIFT - Focus moving mode.",
        "SPACE - Exit the controls screen.",
        "ESC - Quit!",
    ]
    text_lines = [font.render(line, True, (255, 255, 255)) for line in lines]
    line_height = max(font.get_linesize(), 60)
    text_mask = pg.Surface(
        (max(line.get_width() for line in text_lines), line_height * len(lines)),
        pg.SRCALPHA,
    )
    for index, line in enumerate(text_lines):
        text_mask.blit(line, (0, index * line_height))
    title = bigfont.render("Control instructions:", True, (255, 255, 255))
    width, height = screen.get_size()
    scale = min(1, (width - 120) / text_mask.get_width(), (height - 300) / text_mask.get_height())
    if scale < 1:
        text_mask = pg.transform.smoothscale_by(text_mask, scale)
    if title.get_width() > width - 120:
        title = pg.transform.smoothscale_by(title, (width - 120) / title.get_width())
    text_rect = text_mask.get_rect(center=(width // 2, height // 2 + 70))
    title_rect = title.get_rect(midbottom=(width // 2, text_rect.top - 45))
    rainbow = RainbowText(text_mask)
    elapsed = 0

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    return False
                if event.key == pg.K_SPACE:
                    return True

        elapsed += clock.tick(60) / 1000
        screen.fill((0, 0, 0))
        screen.blit(title, title_rect)
        screen.blit(rainbow.render(elapsed), text_rect)
        pg.display.flip()


if __name__ == "__main__":
    run_app()
