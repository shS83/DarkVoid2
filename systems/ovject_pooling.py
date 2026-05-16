class ObjectPool:
	def __init__(self, factory, size):
		self.factory = factory
		self.inactive = [factory() for _ in range(size)]
		self.active = []

	def get(self):
		if self.inactive:
			obj = self.inactive.pop()
		else:
			obj = self.factory()
		self.active.append(obj)
		return obj

	def release(self, obj):
		if obj in self.active:
			self.active.remove(obj)
			self.inactive.append(obj)
