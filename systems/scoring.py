class ScoreSystem:
	def __init__(self):
		self.score = 0
		self.chain = 0
		self.max_chain = 0
		self.chain_timer = 0
		self.chain_timeout = 2.0

	def update(self, dt):
		if self.chain > 0:
			self.chain_timer -= dt
			if self.chain_timer <= 0:
				self.break_chain()

	def add(self, amount):
		self.chain += 1
		self.max_chain = max(self.max_chain, self.chain)
		self.chain_timer = self.chain_timeout
		multiplier = 1 + self.chain * 0.05
		self.score += int(amount * multiplier)

	def break_chain(self):
		self.chain = 0
		self.chain_timer = 0
