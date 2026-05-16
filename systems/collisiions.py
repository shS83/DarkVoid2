import pygame as pg
import config as c


class CollisionSystem:
	def __init__(self, game):
		self.game = game

	def update(self):
		self.player_bullets_vs_enemies()
		self.enemy_bullets_vs_player()
		self.enemies_vs_player()

	def player_bullets_vs_enemies(self):
		hits = pg.sprite.groupcollide(
			self.game.enemies,
			self.game.player_bullets,
			False,
			True
		)

		for enemy, bullets in hits.items():
			damage = sum(getattr(b, "damage", 1) for b in bullets)
			enemy.damage(damage)

	def enemy_bullets_vs_player(self):
		player = self.game.player
		if not player.alive or player.invuln > 0:
			return

		for bullet in self.game.enemy_bullets:
			distance = player.pos.distance_to(bullet.pos)
			if distance < c.PLAYER_HITBOX_RADIUS + bullet.radius:
				self.hit_player()
				bullet.kill()
				break

	def enemies_vs_player(self):
		player = self.game.player
		if not player.alive or player.invuln > 0:
			return

		if pg.sprite.spritecollide(player, self.game.enemies, False):
			self.hit_player()

	def hit_player(self):
		player = self.game.player
		player.invuln = 2.0
		self.game.score.break_chain()
