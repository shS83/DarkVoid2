from enum import Enum


class Event(Enum):
	NOTHING = 0
	INITIATION = 1
	GAMESTART = 2
	NEXTLEVEL = 3
	HIGHSCORE = 4
	DRUMROLL = 5
	GAMEOVER = 6


Event = Event.NOTHING
