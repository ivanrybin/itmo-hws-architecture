import tcod as tc
import time
import random as rnd

from logic.entity import who_blockes
from logic.states import State


class Strategy:
    @staticmethod
    def act(self, target, fov_map, game_map, mobs):
        return []


class PassiveStrategy(Strategy):
    pass


class AggressiveStrategy(Strategy):
    @staticmethod
    def act(self, target, fov_map, game_map, mobs):
        info = []

        if tc.map_is_in_fov(fov_map, self.x, self.y):

            if 2 <= self.get_dist(target) <= 10:
                self.move_astar(target, game_map, mobs)
            elif self.get_dist(target) < 2 and target.stats.hp > 0:
                res = self.stats.attack_target(target)
                info.extend(res)

        return info


class CowardStrategy(Strategy):
    @staticmethod
    def act(self, target, fov_map, game_map, mobs):
        info = []
        if tc.map_is_in_fov(fov_map, self.x, self.y):

            dist = self.get_dist(target)
            if 2 <= dist <= 5:
                if self.x - target.x < 0:
                    if self.y - target.y < 0:
                        self.update_pos(-1, -1, game_map)
                    elif self.y - target.y == 0:
                        self.update_pos(-1, 0, game_map)
                    else:
                        self.update_pos(-1, 1, game_map)
                elif self.x - target.x == 0:
                    if self.y - target.y < 0:
                        self.update_pos(0, -1, game_map)
                    elif self.y - target.y == 0:
                        self.update_pos(-1, 1, game_map)
                    else:
                        self.update_pos(0, 1, game_map)
                else:
                    if self.y - target.y < 0:
                        self.update_pos(1, -1, game_map)
                    elif self.y - target.y == 0:
                        self.update_pos(1, 1, game_map)
                    else:
                        self.update_pos(1, 1, game_map)

        return info
