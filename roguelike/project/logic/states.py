from enum import Enum


class State(Enum):
    PLAYER_TURN = 1
    MOB_TURN = 2
    PLAYER_DEAD = 3
    SHOWING_MENU = 4
    DROP_ITEM = 5

