import pygame as pg


class HUD:
	def __init__(self, game):
		self.game = game
		self.font = pg.font.Font(None, 28)

	def draw(self, screen):
		score = self.game.score.score
		chain = self.game.score.chain
		text = self.font.render(f"Score: {score}  Chain: {chain}", True, (255, 255, 255))
		screen.blit(text, (12, 12))
