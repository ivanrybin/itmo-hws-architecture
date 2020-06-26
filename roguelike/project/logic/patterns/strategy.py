"""
    Паттерн Стратегия.

    Base:    Strategy           - интерфейс стратегии, включающий
                                  единственный метод act(*args, **kwargs)

    Derived: PassiveStrategy    - реализация пассивной стратегии
             AggressiveStrategy - реализация агрессивноый стратегии
             CowardStrategy     - реализация трусливой стратегии
"""
import tcod as tc

from logic.logger import OperationLog
from logic.move import MoveCoords


class PassiveStrategy:
    @staticmethod
    def act(*args, **kwargs):
        return OperationLog()


class AggressiveStrategy:
    min_dist_from_target = 2
    max_dist_from_target = 10

    @staticmethod
    def act(self, target, fov_map, game_map, mobs):
        operation_log = OperationLog()

        if tc.map_is_in_fov(fov_map, self.x, self.y):

            if AggressiveStrategy.min_dist_from_target <= self.get_dist(target) \
                    <= AggressiveStrategy.max_dist_from_target:
                self.move_astar(target, game_map, mobs)
            elif self.get_dist(target) < 2 and target.stats.hp > 0:
                res = self.stats.attack_target(target)
                operation_log.log.extend(res.log)

        return operation_log


class CowardStrategy:
    min_dist_from_target = 2
    max_dist_from_target = 5

    @staticmethod
    def act(self, target, fov_map, game_map, mobs):
        operation_log = OperationLog()

        if tc.map_is_in_fov(fov_map, self.x, self.y):

            dist = self.get_dist(target)
            if CowardStrategy.min_dist_from_target <= dist <= CowardStrategy.max_dist_from_target:
                if self.x - target.x < 0:
                    if self.y - target.y < 0:
                        self.update_pos(MoveCoords.DOWN_LEFT, game_map)
                    elif self.y - target.y == 0:
                        self.update_pos(MoveCoords.LEFT, game_map)
                    else:
                        self.update_pos(MoveCoords.UP_LEFT, game_map)
                elif self.x - target.x == 0:
                    if self.y - target.y < 0:
                        self.update_pos(MoveCoords.DOWN, game_map)
                    elif self.y - target.y == 0:
                        self.update_pos(MoveCoords.UP_LEFT, game_map)
                    else:
                        self.update_pos(MoveCoords.UP, game_map)
                else:
                    if self.y - target.y < 0:
                        self.update_pos(MoveCoords.DOWN_RIGHT, game_map)
                    else:
                        self.update_pos(MoveCoords.UP_RIGHT, game_map)

        return operation_log
