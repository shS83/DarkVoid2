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

	def draw_score(self, screen):
		text = self.font.render(
			f"SCORE {self.game.score}",
			True,
			(240, 240, 255)
		)
		first_text = f"BOSS ARRIVING in {round(self.game.boss_timer)}"
		if self.game.boss_timer <= 1:
			first_text = f"BOSS HP LEFT: {self.game.boss.hp}"
		text2 = self.small_font.render(
			first_text,
			True,
			(255, 50, 50),
		)
		text3 = self.font.render(f"LEVEL {c.level.stage}", True, (255, 200, 255))

		screen.blit(text, (16, 14))
		screen.blit(text2, (16, 40))
		screen.blit(text3, (16, 120))

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
				]
			)
