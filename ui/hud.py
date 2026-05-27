import pygame as pg
import config as c
from entities.level import Level

level = Level()

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
		first_text = f"BOSS ARRIVING in {c.BOSS_TIMER}"
		if c.BOSS_TIMER <= 1 and self.game.boss is not None:
			first_text = f"BOSS HP LEFT: {self.game.boss.hp}"
		text2 = self.small_font.render(
			first_text,
			True,
			(255, 50, 50),
		)
		text3 = self.font.render(f"LEVEL {level.stage}", True, (255, 200, 255))
		text4= ""
		text5= ""
		if self.game.player.shield:
			text4 = self.font.render(f"SHIELD ACTIVE", True, (255, 200, 255))
			text5 = self.font.render(f"SHIELDS LEFT", True, (255, 200, 255))
		if self.game.player.shield:
			for i in range(self.game.player.shield_amount):
				screen.blit(pg.transform.scale(self.game.player.shield_image, (20, 20)), (16 + i * 24, 175))

		screen.blit(text, (16, 14))
		screen.blit(text2, (16, 40))
		screen.blit(text3, (16, 120))

		if self.game.player.shield:
			screen.blit(text4, (16, 180))
			screen.blit(text5, (16, 160))

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
