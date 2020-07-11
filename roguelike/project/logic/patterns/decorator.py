"""
    Паттерн Декоратор.

    MoveDeco(mv_handler) - декорирует обработчки движения игрока,
                           обеспечивая произвольные шаги по направлению движения,
                           подменяя на время player.mv_handler.move() на drunk_move().
"""
from logic.logger import OperationLog
from logic.move import MoveType
from logic.states import State

import random as rnd
import tcod as tc
from time import time


class MoveDeco:
    def __init__(self, move_handler):
        self.mv_handler = move_handler
        self.main_color = move_handler.owner.color
        self.drunk_color = tc.fuchsia
        self.intox_start_time = None
        self.intox_duration = 7

    def set_intox_start_time(self, value):
        self.intox_start_time = value
        self.mv_handler.owner.color = self.drunk_color

    def move(self, move_type, game_map, mobs, curr_state):
        start_t = self.intox_start_time

        # проверяет не вышло ли время интоксикации
        if start_t and time() - self.intox_start_time <= self.intox_duration:
            return MoveDeco.drunk_move(self.mv_handler, self.mv_handler.owner, move_type, game_map, mobs, curr_state)

        self.intox_start_time = None
        if self.mv_handler.owner.color == self.drunk_color:
            self.mv_handler.owner.color = self.main_color
        return self.mv_handler.move(move_type, game_map, mobs, curr_state)

    @staticmethod
    def drunk_move(mv_handler, mv_owner, move_type, game_map, mobs, curr_state):

        if curr_state.value != State.PLAYER_TURN:
            return OperationLog()

        dx, dy = mv_handler.mv_types[move_type]

        if game_map.is_cell_blocked(mv_owner.x + dx, mv_owner.y + dy):
            return OperationLog()

        victim = mv_owner.who_blocks(mobs[1:], mv_owner.x + dx, mv_owner.y + dy)

        if victim:
            return mv_owner.stats.attack_target(victim)
        else:
            # делаем случайны ход по диагонали в направлении движения игрока
            if rnd.random() < 0.5:
                if move_type in [MoveType.LEFT, MoveType.RIGHT]:
                    mv_owner.update_pos((dx, dy + 1), game_map)
                elif move_type in [MoveType.UP, MoveType.DOWN]:
                    mv_owner.update_pos((dx + 1, dy), game_map)
            else:
                if move_type in [MoveType.LEFT, MoveType.RIGHT]:
                    mv_owner.update_pos((dx, dy - 1), game_map)
                elif move_type in [MoveType.UP, MoveType.DOWN]:
                    mv_owner.update_pos((dx - 1, dy), game_map)

        curr_state.value = State.MOB_TURN

        print(mv_owner.x, mv_owner.y)

        return OperationLog()
