from pygame import Vector2


def wrap_position(pos, rect, margin=0):
	return Vector2(
		pos.x % (rect.width + margin),
		pos.y % (rect.height + margin)
	)
