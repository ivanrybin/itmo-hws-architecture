from enum import Enum


class State(Enum):
    PLAYER_TURN = 1
    MOB_TURN = 2
    PLAYER_DEAD = 3
    SHOW_MENU = 4
