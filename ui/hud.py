import pygame as pg
import config as c


class HUD:
	def __init__(self, game):
		self.game = game
		self.font = pg.font.Font(None, 32)
		self.small_font = pg.font.Font(None, 22)

	def draw(self, screen):
		self.draw_score(screen)
		self.draw_lives(screen)
		self.draw_boss_bar(screen)
		if self.game.game_over or not self.game.player.visible:
			self.draw_highscores(screen)

	def draw_score(self, screen):
		text = self.font.render(f"SCORE {self.game.score}", True, (240, 240, 255))
		first_text = ""

		text2 = self.small_font.render(
			first_text,
			True,
			(255, 50, 50),
		)
		text3 = self.font.render(
			f"STAGE {self.game.level.stage}", True, (255, 200, 255)
		)
		text4 = ""
		text5 = ""
		if self.game.player.shield:
			text4 = self.font.render(f"SHIELD ACTIVE", True, (255, 200, 255))
			text5 = self.font.render(f"SHIELDS LEFT", True, (255, 200, 255))
		if self.game.player.shield:
			for i in range(self.game.player.shield_amount):
				screen.blit(
                    pg.transform.scale(self.game.player.shield_image, (20, 20)),
                    (16 + i * 24, 175),
			)

		screen.blit(text, (16, 14))
		screen.blit(text2, (16, 40))
		screen.blit(text3, (16, 120))

		if self.game.player.shield_active:
			screen.blit(text4, (16, 210))
		if self.game.player.shield:
			screen.blit(text5, (16, 145))

	def draw_lives(self, screen):
		label = self.small_font.render("ENERGY", True, (220, 220, 255))
		screen.blit(label, (16, 60))

		for i in range(self.game.player.lives):
			x = 16 + i * 24
			y = 78

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
			name_text = self.small_font.render(f"{boss.name}", True, (240, 240, 255))
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
	x = c.WIDTH - 210
	y = 20

	title = self.small_font.render("HIGH SCORES", True, (240, 220, 255))
	screen.blit(title, (x, y))

	y += 26
	if self.game.killed_by:
		killer_text = self.small_font.render(
			self.game.killed_by,
			True,
			(230, 180, 255)
		)

		killer_rect = killer_text.get_rect(
			center=(c.WIDTH // 2, c.HEIGHT // 2 + 70)
		)

		screen.blit(killer_text, killer_rect)

	for index, entry in enumerate(self.game.highscores.entries[:8], start=1):
		text = self.small_font.render(
			f"{index}. {entry['name']} {entry['score']}",
			True,
			(210, 210, 240)
		)

		screen.blit(text, (x, y))
		y += 22