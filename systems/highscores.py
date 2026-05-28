import json
from pathlib import Path


class HighScoreTable:
	def __init__(self, path, max_entries=10):
		self.path = Path(path)
		self.max_entries = max_entries
		self.entries = []
		self.load()

	def load(self):
		if not self.path.exists():
			self.entries = []
			return

		try:
			with open(self.path, "r", encoding="utf-8") as file:
				self.entries = json.load(file)
		except (json.JSONDecodeError, OSError):
			self.entries = []

	def save(self):
		self.path.parent.mkdir(parents=True, exist_ok=True)

		with open(self.path, "w", encoding="utf-8") as file:
			json.dump(self.entries, file, indent=4)

	def add_score(self, name, score, level=1, killed_by="Unknown"):
		entry = {
			"name": name,
			"score": int(score),
			"level": int(level),
			"killed_by": killed_by,
		}

		self.entries.append(entry)

		self.entries.sort(
			key=lambda item: item["score"],
			reverse=True
		)

		self.entries = self.entries[:self.max_entries]

		self.save()

	def is_high_score(self, score):
		if len(self.entries) < self.max_entries:
			return True

		return score > self.entries[-1]["score"]