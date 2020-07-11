from enum import Enum
from collections import namedtuple

from logic.logger import OperationLog
from logic.states import State


class MoveType(Enum):
    LEFT = 1
    RIGHT = 2
    UP = 3
    DOWN = 4


Vec2D = namedtuple('Point', ['x', 'y'])


class MoveCoords:
    LEFT = Vec2D(-1, 0)
    RIGHT = Vec2D(1, 0)
    UP = Vec2D(0, -1)
    UP_LEFT = Vec2D(-1, -1)
    UP_RIGHT = Vec2D(1, -1)
    DOWN = Vec2D(0, 1)
    DOWN_LEFT = Vec2D(-1, 1)
    DOWN_RIGHT = Vec2D(1, 1)


class MoveHandler:
    def __init__(self, owner):
        self.owner = owner
        self.mv_types = {MoveType.LEFT: MoveCoords.LEFT,
                         MoveType.RIGHT: MoveCoords.RIGHT,
                         MoveType.UP: MoveCoords.UP,
                         MoveType.DOWN: MoveCoords.DOWN}

    def move(self, mv_type, game_map, mobs, curr_state):
        print(curr_state.value)
        if curr_state.value != State.PLAYER_TURN:
            return OperationLog()

        dx, dy = self.mv_types[mv_type]

        if game_map.is_cell_blocked(self.owner.x + dx, self.owner.y + dy):
            return OperationLog()

        victim = self.owner.who_blocks(mobs[1:], self.owner.x + dx, self.owner.y + dy)

        if victim:
            return self.owner.stats.attack_target(victim)
        else:
            self.owner.update_pos(self.mv_types[mv_type], game_map)

        curr_state.value = State.MOB_TURN

        print(self.owner.x, self.owner.y)

        return OperationLog()
