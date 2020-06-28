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
from abc import abstractmethod


class Strategy:

    @abstractmethod
    def act(self, *args, **kwargs):
        pass


class PassiveStrategy(Strategy):

    def act(self, *args, **kwargs):
        return OperationLog()


class AggressiveStrategy(Strategy):
    min_dist_from_target = 2
    max_dist_from_target = 10

    def act(self, mob, target, fov_map, game_map, mobs):
        operation_log = OperationLog()

        if not fov_map or tc.map_is_in_fov(fov_map, mob.x, mob.y):
            if AggressiveStrategy.min_dist_from_target <= mob.get_dist(target) \
                    <= AggressiveStrategy.max_dist_from_target:
                mob.move_astar(target, game_map, mobs)
            elif mob.stats and mob.get_dist(target) < 2 and target.stats.hp > 0:
                res = mob.stats.attack_target(target)
                operation_log.log.extend(res.log)

        return operation_log


class CowardStrategy(Strategy):
    min_dist_from_target = 2
    max_dist_from_target = 5

    def act(self, mob, target, fov_map, game_map, mobs):
        operation_log = OperationLog()

        if not fov_map or tc.map_is_in_fov(fov_map, mob.x, mob.y):

            dist = mob.get_dist(target)
            if CowardStrategy.min_dist_from_target <= dist <= CowardStrategy.max_dist_from_target:
                if mob.x - target.x < 0:
                    if mob.y - target.y < 0:
                        mob.update_pos(MoveCoords.DOWN_LEFT, game_map)
                    elif mob.y - target.y == 0:
                        mob.update_pos(MoveCoords.LEFT, game_map)
                    else:
                        mob.update_pos(MoveCoords.UP_LEFT, game_map)
                elif mob.x - target.x == 0:
                    if mob.y - target.y < 0:
                        mob.update_pos(MoveCoords.DOWN, game_map)
                    elif mob.y - target.y == 0:
                        mob.update_pos(MoveCoords.UP_LEFT, game_map)
                    else:
                        mob.update_pos(MoveCoords.UP, game_map)
                else:
                    if mob.y - target.y < 0:
                        mob.update_pos(MoveCoords.DOWN_RIGHT, game_map)
                    else:
                        mob.update_pos(MoveCoords.UP_RIGHT, game_map)

        return operation_log
