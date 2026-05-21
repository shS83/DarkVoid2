import pygame as pg
import pygame.gfxdraw
import os
import config as c


class HighScore:
	def __init__(self, name: str = "John", score: int = 10):
		self.name = name
		self.score = score
		self.ASSET_DIR = f'{c.HOME_DIR}/assets'
		self.empty = pg.image.load(f'{self.ASSET_DIR}/tyhja.png')
		self.new_hs_text = pg.image.load(f'{self.ASSET_DIR}/highscore_text.png')
		self.tausta = pg.image.load(f'{self.ASSET_DIR}/pelitausta_2.png')

		self.font = pg.font.Font(f'{self.ASSET_DIR}/JetBrainsMonoNerdFont-SemiBold.ttf', 18)
		self.die_font = pg.font.Font(f'{self.ASSET_DIR}/JetBrainsMonoNerdFont-SemiBold.ttf', 100)
		self.hs_font = self.font

		self.x_res = c.WIDTH
		self.y_res = c.HEIGHT
		self.timer = pygame.time.Clock()
		self.font = self.hs_font
		HOME_DIR = c.HOME_DIR

		self.high_scores = []
		self.new_score = None
		self.input_text = ""
		self.finished_typing = False
		self.typing_name = False

		def load_scores(self):
			if len(self.high_scores) < 1:
				handle = open(f"{HOME_DIR}/gemfall_highscores.txt", "r")
				for line in handle:
					self.high_scores.append(line.rstrip())
				return True
			return False

		def check_score(self, highscore):
			new_score = "NO"

			for e in range(0, len(self.high_scores) - 1):
				user, scoreamount = self.high_scores[e].split(" ")
				if self.highscore >= int(scoreamount):
					self.finished_typing = False
					self.new_score = e
					return True
			return False

		def fix_scores(self, index, user, highscore):

			for e in range(0, len(self.high_scores) - 1):
				if e == self.index:
					self.high_scores.insert(index, f"{self.user} {self.highscore}")
					self.high_scores.pop()
					return True
			return False

		def save_scores(self):
			try:
				handle = open(f"{HOME_DIR}/gemfall_highscores.txt", "w")
				for scr in self.high_scores:
					handle.write(scr + "\n")
				return True
			except OSError:
				print("Could not open/read highscore file")
				return False

		def blend_fill(self, screen, fade_to):
			color = fade_to
			screen.fill((color, color, color), None, special_flags=pygame.BLEND_RGBA_SUB)

		def draw_input(self, color):
			size_surf = self.font.render("MMMMMMMMMM", True, (0, 0, 0))
			font_w = size_surf.get_width()
			font_h = size_surf.get_height()
			rect_w = font_w + 20
			rect_h = font_h + 20
			self.text_surface = self.font.render(self.input_text, True, (255, 255, 255))
			self.alpha_surface = pg.Surface((rect_w, rect_h))
			outer_rect = pg.Rect(0, 0, rect_w, rect_h)
			input_rect = pg.Rect(5, 5, rect_w - 10, rect_h - 10)
			pg.draw.rect(self.alpha_surface, (255, 255, 255), outer_rect)
			pg.draw.rect(self.alpha_surface, color, input_rect)
			self.alpha_surface.set_alpha(160)
			input_x = c.WIDTH / 2 - self.text_surface.get_width() / 2
			blit_x = c.WIDTH / 2 - self.alpha_surface.get_width() / 2
			blit_y = c.HEIGHT - self.alpha_surface.get_height() / 2 - 200
			self.font_surface = self.font.render("Please enter your name:", True, (255, 255, 255))
			text_blit_x = c.WIDTH / 2 - self.font_surface.get_width() / 2
			c.screen.blit(self.font_surface, (text_blit_x, blit_y - 50))
			c.screen.blit(self.alpha_surface, (blit_x, blit_y))
			c.screen.blit(self.text_surface, (input_x, blit_y + 8))

		def scores(self, fontname, fsize):
			self.hs_font = pygame.font.Font(f"{HOME_DIR}/assets/{fontname}", int(round(fsize * 1.2)))
			self.score_font = pygame.font.Font(f"{HOME_DIR}/assets/{fontname}", fsize)
			self.hstext = "HALL OF FAME"
			self.hsblit = self.hs_font.render(self.hstext, True, (255, 255, 255))
			self.hsize = self.hs_font.size(self.hstext)
			c.screen.blit(self.hsblit, (c.WIDTH / 2 - self.hsize[0] / 2, c.HEIGHT / 10))
			self.maxlen = len(self.high_scores)

			if self.maxlen > 10:
				self.maxlen = 10

			for i in range(0, self.maxlen):
				self.user, self.score = self.high_scores[i].split(" ")
				usize = self.score_font.size(self.user)
				ssize = self.score_font.size(self.score)
				self.userblit = self.score_font.render(self.user, True, (255, 255, 255))
				self.scoreblit = self.score_font.render(self.score, True, (255, 255, 255))
				c.screen.blit(self.userblit, (c.WIDTH / 2 - 175, c.HEIGHT / 10 + 50 + (usize[1] + 30 * i)))
				c.screen.blit(self.scoreblit,
				              (c.WIDTH / 2 + (175 - ssize[0]), c.HEIGHT / 10 + 50 + (ssize[1] + 30 * i)))
