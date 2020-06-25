"""
    Паттерн Декоратор.

    intoxicating_deco(player)  - декорирует движение игрока
                                 на произвольные шаги по направлению движения,
                                 подменяя на время player.move() на drunk_move(),
                                 с помощью питоновских диктов.
"""

from logic.player import who_blocks
from logic.states import State

import random as rnd
import tcod as tc
from time import time


def intoxicating_deco(player):
    # deco func
    def drunk_move(self, move_type, game_map, mobs):
        # проверяет не вышло ли время интоксикации
        # если вышло - возвращает исходную функцию движения на место
        start_t = self.stats.intox_start_time
        if start_t and time() - start_t >= 7:
            self.move = self.__old_move
            self.color = self.__old_color
            self.stats.intox_start_time = None
            return self.move(self, move_type, game_map, mobs)

        if game_map.state != State.PLAYER_TURN:
            return []

        dx, dy = self.mv_types[move_type]

        if game_map.is_cell_blocked(self.x + dx, self.y + dy):
            return []

        victim = who_blocks(self, mobs[1:], self.x + dx, self.y + dy)

        if victim:
            return self.stats.attack_target(victim)
        else:
            # делаем случайны ход по диагонали в направлении движения игрока
            if rnd.random() < 0.5:
                if move_type in ['LEFT', 'RIGHT']:
                    self.update_pos(dx, dy + 1, game_map)
                elif move_type in ['UP', 'DOWN']:
                    self.update_pos(dx + 1, dy, game_map)
            else:
                if move_type in ['LEFT', 'RIGHT']:
                    self.update_pos(dx, dy - 1, game_map)
                elif move_type in ['UP', 'DOWN']:
                    self.update_pos(dx - 1, dy, game_map)

        game_map.state = State.MOB_TURN

        print(self.x, self.y)

        return []

    player.__old_move = player.move
    player.__old_color = player.color
    player.move = drunk_move
    player.color = tc.fuchsia
