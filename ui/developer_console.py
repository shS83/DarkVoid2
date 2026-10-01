from collections import deque

import pygame as pg


class DeveloperConsole:
    def __init__(self, game, font):
        self.game = game
        self.font = font
        self.open = False
        self.progress = 0.0
        self.input = ""
        self.history = []
        self.history_index = 0
        self.draft = ""
        self.output = deque(maxlen=200)
        self.scroll = 0
        self.cursor_timer = 0.0

    @property
    def active(self):
        return self.open or self.progress > 0

    @staticmethod
    def is_toggle(event):
        return event.type == pg.KEYDOWN and (
            getattr(event, "unicode", "") == "\u00a7"
            or event.key == pg.K_BACKQUOTE
            or getattr(event, "scancode", None) == getattr(pg, "KSCAN_GRAVE", 53)
        )

    def toggle(self):
        self.open = not self.open
        if self.open:
            self.cursor_timer = 0.0
            pg.key.start_text_input()
        else:
            pg.key.stop_text_input()
            if self.game.entering_highscore:
                pg.key.start_text_input()

    def update(self, dt):
        if self.open:
            self.cursor_timer = (self.cursor_timer + dt) % 1.0
        target = 1.0 if self.open else 0.0
        step = dt / 0.22
        if self.progress < target:
            self.progress = min(target, self.progress + step)
        else:
            self.progress = max(target, self.progress - step)

    def write(self, text):
        self.output.extend(str(text).splitlines())
        self.scroll = 0

    def execute(self):
        command = self.input.strip()
        self.input = ""
        self.cursor_timer = 0.0
        if not command:
            return
        self.write("> " + command)
        if not self.history or self.history[-1] != command:
            self.history.append(command)
        self.history_index = len(self.history)
        self.draft = ""
        if command.lower() == "clear":
            self.output.clear()
            return
        try:
            self.write(self.game.execute_console_command(command))
        except (ValueError, OSError, pg.error) as error:
            self.write("Error: " + str(error))

    def handle_event(self, event):
        if self.is_toggle(event):
            if not getattr(event, "repeat", False):
                self.toggle()
            return True
        if not self.active:
            return False
        if not self.open:
            return True
        if event.type == pg.TEXTINPUT:
            # SDL may send the opening key as TEXTINPUT in the same event batch.
            clean = "".join(char for char in event.text if char.isprintable() and char not in "\u00a7`")
            self.input = (self.input + clean)[:128]
            self.history_index = len(self.history)
            if clean:
                self.cursor_timer = 0.0
        elif event.type == pg.KEYDOWN:
            self.cursor_timer = 0.0
            if event.key == pg.K_ESCAPE:
                self.toggle()
            elif event.key in (pg.K_RETURN, pg.K_KP_ENTER):
                self.execute()
            elif event.key == pg.K_BACKSPACE:
                self.input = self.input[:-1]
            elif event.key == pg.K_UP:
                if self.history_index == len(self.history):
                    self.draft = self.input
                self.history_index = max(0, self.history_index - 1)
                if self.history:
                    self.input = self.history[self.history_index]
            elif event.key == pg.K_DOWN:
                self.history_index = min(len(self.history), self.history_index + 1)
                self.input = self.draft if self.history_index == len(self.history) else self.history[self.history_index]
            elif event.key == pg.K_PAGEUP:
                self.scroll = min(len(self.output), self.scroll + 5)
            elif event.key == pg.K_PAGEDOWN:
                self.scroll = max(0, self.scroll - 5)
        elif event.type == pg.MOUSEWHEEL:
            self.scroll = max(0, min(len(self.output), self.scroll + event.y * 3))
        return True

    def draw(self, screen):
        if not self.active:
            return
        width, screen_height = screen.get_size()
        height = screen_height // 2
        eased = self.progress * self.progress * (3 - 2 * self.progress)
        top = screen_height - round(height * eased)
        panel = pg.Surface((width, height), pg.SRCALPHA)
        panel.fill((0, 0, 0, 128))
        screen.blit(panel, (0, top))
        clip = screen.get_clip()
        screen.set_clip(pg.Rect(0, top, width, height))
        line_height = self.font.get_linesize()
        prompt_y = top + height - line_height - 16
        available_width = width - 48
        visible_input = self.input
        while visible_input and self.font.size("> " + visible_input + "_")[0] > available_width:
            visible_input = visible_input[1:]
        prompt = self.font.render("> ", True, (0, 255, 0))
        text = self.font.render(visible_input, True, (255, 255, 255))
        text_x = 24 + prompt.get_width()
        screen.blit(prompt, (24, prompt_y))
        screen.blit(text, (text_x, prompt_y))
        if self.open and self.cursor_timer < 0.5:
            cursor = self.font.render("_", True, (255, 255, 255))
            screen.blit(cursor, (text_x + text.get_width(), prompt_y))
        columns = max(1, available_width // max(1, self.font.size("M")[0]))
        wrapped = []
        for line in self.output:
            wrapped.extend(line[index:index + columns] for index in range(0, max(1, len(line)), columns))
        visible_lines = max(0, (height - 48) // line_height - 1)
        self.scroll = min(self.scroll, max(0, len(wrapped) - visible_lines))
        end = len(wrapped) - self.scroll
        for index, line in enumerate(reversed(wrapped[max(0, end - visible_lines):end])):
            y = prompt_y - (index + 1) * line_height
            if line.startswith("> "):
                screen.blit(prompt, (24, y))
                screen.blit(self.font.render(line[2:], True, (255, 255, 255)), (text_x, y))
            else:
                screen.blit(self.font.render(line, True, (255, 255, 255)), (24, y))
        screen.set_clip(clip)
