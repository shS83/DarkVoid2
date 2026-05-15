from enum import Enum


class State(Enum):
	""" The name of the game """
	INTRO = 0
	WAITINGFORUSER = 1
	PLAYING = 2
	DIED_WATCHING_ROCKS = 3
	WAITINGFORGAME = 4
	NEXTLEVEL = 5
	HIGHSCORETYPING = 6
	HIGHSCORES = 7
