class Boss(pg.sprite.Sprite):
	def __init__(self, game, pos):
		super().__init__()
		self.game = game
		self.pos = pg.Vector2(pos)
		self.hp = 1000
		self.phase_index = 0
		self.phase_timer = 0
		self.phases = [
			self.phase_intro,
			self.phase_radial,
			self.phase_spiral,
			self.phase_desperation,
		]

	def update(self, dt):
		self.phase_timer += dt
		self.phases[self.phase_index](dt)

	def next_phase(self):
		self.phase_index += 1
		self.phase_timer = 0

	def phase_intro(self, dt):
		pass

	def phase_radial(self, dt):
		pass

	def phase_spiral(self, dt):
		pass

	def phase_desperation(self, dt):
		pass
