import pygame as pg
import config as c
from pathlib import Path
from pygame import gfxdraw

class HUD:
	def __init__(self, game):
		self.game = game
		self.font = pg.font.Font(None, 32)
		self.small_font = pg.font.Font(None, 22)
		self.nerd_font = pg.font.Font(Path(c.HOME_DIR, "assets", "fonts", "MonaspiceXeNerdFontPropo-Light.otf"), 128)
		self.medium_nerd = pg.font.Font(Path(c.HOME_DIR, "assets", "fonts", "MonaspiceXeNerdFontPropo-Light.otf"), 56)
		self.small_nerd = pg.font.Font(Path(c.HOME_DIR, "assets", "fonts", "MonaspiceXeNerdFontPropo-Light.otf"), 20)
		self.tiny_nerd = pg.font.Font(Path(c.HOME_DIR, "assets", "fonts", "MonaspiceXeNerdFontPropo-Light.otf"), 16)
		self.vulcan_rect = pg.Surface((300, 50), pg.SRCALPHA, 32)

	def draw(self, screen):
		if not self.game.game_over and self.game.player.visible:
			self.draw_score(screen)
			self.draw_lives(screen)
			self.draw_boss_bar(screen)
			self.draw_vulcan_overheat(screen)

	def overheat_color(self, ratio):
		ratio = max(0, min(1, ratio))

		if ratio < 0.5:
			# green -> yellow
			t = ratio / 0.5

			r = int(80 + (255 - 80) * t)
			g = 220
			b = 60

		else:
			# yellow -> red
			t = (ratio - 0.5) / 0.5

			r = 255
			g = int(220 + (40 - 220) * t)
			b = int(60 + (40 - 60) * t)

		return (r, g, b)

	def draw_vulcan_overheat(self, screen):
		bar_x = c.WIDTH - 330
		bar_y = 50
		bar_width = 300
		bar_height = 24

		max_heat = self.game.player.vulcan_heat_max
		cooling_rate = self.game.player.vulcan_cool_rate
		heat = self.game.player.vulcan_heat
		#
		# if not self.game.player.vulcan_overheated:
		# 	text_surf = self.small_nerd.render(
		# 		f"VULCAN OVERHEAT {heat:.1f}",
		# 		True,
		# 		(255, 255, 255)
		# 	)
		# 	text_rect = text_surf.get_rect(
		# 		center=(bar_x + bar_width // 2, bar_y - 16)
		# 	)
		# 	screen.blit(text_surf, text_rect)

		# You should adjust this to your actual max overheat value
		max_overheat = self.game.player.vulcan_heat_max
		heat_ratio = self.game.player.vulcan_heat / self.game.player.vulcan_heat_max
		heat_ratio = max(0, min(1, heat_ratio))
		fill_color = self.overheat_color(heat_ratio)
		overheat = False

		if heat <= 0:
			overheat = False
			heat = 0
			max_overheat = 3
		elif heat >= max_overheat:
			overheat = True
			heat = max_overheat

		if self.game.player.vulcan_overheated:
			label = "VULCAN OVERHEATED"
		elif heat_ratio > 0:
			label = f"VULCAN HEAT {heat_ratio * 100:.0f}%"
		else:
			label = "VULCAN READY"

		text_surf = self.small_nerd.render(
			f"{label} {heat:.1f}",
			True,
			(255, 255, 255)
		)

		fill_width = int(bar_width * heat_ratio)

		fill_rect = pg.Rect(
			bar_x + 3,
			bar_y + 3,
			max(0, fill_width - 6),
			bar_height - 6
		)

		pg.draw.rect(
			screen,
			fill_color,
			fill_rect,
			border_radius=1
		)

		text_rect = text_surf.get_rect(
			center=(bar_x + bar_width // 2, bar_y - 16)
		)

		screen.blit(text_surf, text_rect)

		back_rect = pg.Rect(bar_x, bar_y, bar_width, bar_height)
		fill_width = int(bar_width * heat_ratio)

		fill_rect = pg.Rect(
			bar_x + 3,
			bar_y + 3,
			max(0, fill_width - 6),
			bar_height - 6
		)


		pg.draw.rect(
			screen,
			(220, 220, 255),
			back_rect,
			width=2,
			border_radius=1
		)

		pg.draw.rect(
			screen,
			fill_color,
			fill_rect,
			border_radius=1
		)



	def draw_score(self, screen):
		text = self.small_nerd.render(f"SCORE {self.game.score}", True, (240, 240, 255))
		first_text = ""

		text2 = self.small_font.render(
			first_text,
			True,
			(255, 50, 50),
		)
		text3 = self.small_nerd.render(
			f"STAGE {self.game.level.stage}", True, (255, 200, 255)
		)
		text4 = ""
		text5 = ""
		if self.game.player.shield:
			text4 = self.small_nerd.render(f"SHIELD ACTIVE", True, (100, 100, 255))
			text5 = self.small_nerd.render(f"SHIELDS LEFT", True, (255, 200, 255))
		if self.game.player.shield:
			for i in range(self.game.player.shield_amount):
				screen.blit(
                    pg.transform.scale(self.game.player.shield_image, (20, 20)),
                    (16 + i * 24, 195),
			)

		screen.blit(text, (16, 50))
		screen.blit(text2, (16, 26))
		screen.blit(text3, (16, 14))

		if self.game.player.shield_active:
			screen.blit(text4, (16, 220))
		if self.game.player.shield:
			screen.blit(text5, (16, 160))

	def draw_lives(self, screen):
		label = self.small_nerd.render("ENERGY", True, (220, 220, 255))
		screen.blit(label, (16, 85))

		for i in range(self.game.player.lives):
			x = 16 + i * 24
			y = 130

			pg.draw.polygon(
			screen,
			(120, 220, 255),
			[
                    (x + 10, y),
                    (x + 20, y + 20),
                    (x + 10, y + 15),
                    (x, y + 20),
			],
			)

	def draw_boss_bar(self, screen):
		boss = self.game.boss

		if boss is None or not c.BOSS_TIME:
			return

		if boss is None:
			return

		if not hasattr(boss, "hp") or not hasattr(boss, "max_hp"):
			return

		if boss.max_hp <= 0:
			return

		ratio = max(0, boss.hp / boss.max_hp)

		bar_width = 520
		bar_height = 24

		x = (c.WIDTH - bar_width) // 2
		y = c.HEIGHT - 42

		# Dark backdrop
		bg_rect = pg.Rect(x, y, bar_width, bar_height)
		pg.draw.rect(screen, (20, 20, 30), bg_rect, border_radius=10)

		# Outer frame
		pg.draw.rect(screen, (180, 180, 220), bg_rect, width=2, border_radius=10)

		# Fill width
		fill_width = int((bar_width - 6) * ratio)
		fill_rect = pg.Rect(x + 3, y + 3, fill_width, bar_height - 6)

		# Color changes by remaining health
		if ratio > 0.6:
			fill_color = (180, 40, 220)  # purple
			glow_color = (255, 120, 255)
		elif ratio > 0.3:
			fill_color = (255, 140, 40)  # orange
			glow_color = (255, 220, 120)
		else:
			fill_color = (220, 40, 40)  # red
			glow_color = (255, 120, 120)

		if fill_width > 0:
			pg.draw.rect(screen, fill_color, fill_rect, border_radius=8)

			# inner highlight
			highlight_rect = pg.Rect(
				fill_rect.x, fill_rect.y, fill_rect.width, max(4, fill_rect.height // 3)
			)
			pg.draw.rect(screen, glow_color, highlight_rect, border_radius=8)

		# Boss name text
		if hasattr(boss, "name"):
			name_text = self.small_nerd.render(f"{boss.name}", True, (240, 240, 255))
			name_rect = name_text.get_rect(midbottom=(c.WIDTH // 2, y - 4))
			screen.blit(name_text, name_rect)

		segments = 20
		segment_width = bar_width / segments

		for i in range(1, segments):
			sx = int(x + i * segment_width)
			pg.draw.line(screen, (60, 60, 90), (sx, y + 2), (sx, y + bar_height - 2), 1)

		glow = pg.Surface((bar_width + 20, bar_height + 20), pg.SRCALPHA)
		pg.draw.rect(
			glow,
			(12, 4, 18, 10),
			glow.get_rect(),
			border_radius=10
		)
		screen.blit(glow, (x - 10, y - 10), special_flags=pg.BLEND_RGBA_ADD)

	def draw_highscores(self, screen):
		overlay = pg.Surface((c.WIDTH, c.HEIGHT), pg.SRCALPHA)
		overlay.fill((0, 0, 0, 185))
		screen.blit(overlay, (0, 0))

		panel_width = 640
		panel_height = 640

		panel_x = (c.WIDTH - panel_width) // 2
		panel_y = (c.HEIGHT - panel_height) // 2

		panel = pg.Surface((panel_width, panel_height), pg.SRCALPHA)
		panel.fill((10, 8, 20, 225))

		panel_rect = pg.Rect(panel_x, panel_y, panel_width, panel_height)

		screen.blit(panel, panel_rect.topleft)

		pg.draw.rect(screen, (190, 160, 255), panel_rect, width=3, border_radius=14)
		pg.draw.rect(screen, (80, 30, 130), panel_rect.inflate(-10, -10), width=1, border_radius=10)

		title = self.medium_nerd.render("HIGH SCORES", True, (255, 230, 150))
		title_rect = title.get_rect(center=(c.WIDTH // 2, panel_y + 42))
		screen.blit(title, title_rect)

		y = panel_y + 120

		for index, entry in enumerate(self.game.highscores.entries[:8], start=1):
			name = entry.get("name", "???")
			score = entry.get("score", 0)
			level = entry.get("level", 1)
			killed_by = entry.get("killed_by", "the Illithids")

			main_line = f"{index:02}. {name:<12} {score:>8}  STAGE {level}"

			color = (240, 240, 255)

			if index == 1:
				color = (255, 220, 120)

			text = self.small_nerd.render(main_line, True, color)
			text_rect = text.get_rect(center=(c.WIDTH // 2, y))
			screen.blit(text, text_rect)

			y += 30

			killer_line = f"killed by {killed_by}"

			killer_text = self.tiny_nerd.render(
				killer_line,
				True,
				(170, 150, 210)
			)

			killer_rect = killer_text.get_rect(center=(c.WIDTH // 2, y))
			screen.blit(killer_text, killer_rect)

			y += 30

		if self.game.entering_highscore:
			self.draw_highscore_input(screen, panel_y + panel_height - 90)
		else:
			hint = self.small_nerd.render("PRESS ESC TO QUIT OR SPACE TO RESTART", True, (170, 170, 210))
			hint_rect = hint.get_rect(center=(c.WIDTH // 2, panel_y + panel_height - 32))
			screen.blit(hint, hint_rect)

	def draw_highscore_input(self, screen, y):
		prompt = self.small_nerd.render("ENTER YOUR NAME", True, (255, 230, 120))
		prompt_rect = prompt.get_rect(center=(c.WIDTH // 2, y))
		screen.blit(prompt, prompt_rect)

		name = self.game.highscore_name

		if int(pg.time.get_ticks() / 400) % 2 == 0:
			name += "_"

		box_width = 280
		box_height = 42

		box = pg.Rect(
			(c.WIDTH - box_width) // 2,
			y + 24,
			box_width,
			box_height
		)

		pg.draw.rect(screen, (0, 0, 0), box, border_radius=8)
		pg.draw.rect(screen, (120, 220, 255), box, width=2, border_radius=8)

		name_text = self.small_nerd.render(name, True, (120, 220, 255))
		name_rect = name_text.get_rect(center=box.center)
		screen.blit(name_text, name_rect)