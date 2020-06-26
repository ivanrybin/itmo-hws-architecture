"""
    Entity - базовый класс для всех сущностей игры.
"""

import math
import time
import tcod as tc
import numpy as np
from enum import Enum

from engine.render import RenderOrder
from logic.patterns.strategy import PassiveStrategy


class EntityType(Enum):
    PLAYER = 1
    MOB = 2
    ITEM = 3
    HEALTH_PTN = 4
    INTOX_PTN = 5
    ARMOUR = 6


class Entity:
    def __init__(self, x, y, screen_width, screen_height, char, color, name,
                 stats=None, game_map=None, strategy=PassiveStrategy,
                 is_blocking=True, render_order=RenderOrder.ALIVE_ENTITY,
                 item=None, inventory=None, entity_type=None,
                 move_handler=None):
        self.x = x
        self.y = y
        self.sw = screen_width
        self.sh = screen_height
        if isinstance(char, int):
            self.char = char
        if isinstance(char, str):
            self.char = ord(char)
        self.color = color
        self.name = name
        self.stats = stats
        self.map = game_map
        self.strategy = strategy
        self.is_blocking = is_blocking
        self.render_order = render_order
        self.item = item
        self.inventory = inventory
        self.type = entity_type
        self.main_color = color
        self.mv_handler = move_handler

        if self.item:
            self.item.owner = self
        if self.inventory:
            self.inventory.owner = self

    def serialize(self):
        data = {
            'x': self.x,
            'y': self.y,
            'scr_wd': self.sw,
            "scr_ht": self.sh,
            'ch': self.char,
            'clr': self.color,
            'name': self.name,
            'strat': self.strategy.__name__,
            'is_block': self.is_blocking,
            'render_ord': self.render_order.value,
            'main_clr': self.main_color,
            'stats': None,
            'item': None,
            'inventory': None,
            'type': None
        }

        if self.stats:
           data['stats'] = self.stats.serialize()
        if self.item:
            data['item'] = self.item.serialize()
        if self.inventory:
            data['inventory'] = self.inventory.serialize()
        if self.type:
            data['type'] = self.type.value

        return data

    def who_blocks(self, mobs, dest_x, dest_y):
        for mob in mobs:
            if mob != self and mob.x == dest_x and mob.y == dest_y and mob.stats and mob.is_blocking:
                return mob
        return None

    def __update_axis(self, is_x, axis, delta):
        length = self.sh
        if is_x:
            length = self.sw

        if 0 <= axis + delta < length:
            if is_x:
                delta = self.x + delta
            else:
                delta = self.y + delta
        elif axis + delta >= length:
            delta = length - 1
        elif axis + delta < 0:
            delta = 0

        if is_x:
            self.x = delta
        else:
            self.y = delta

    def update_pos(self, move_coords, game_map):
        dx, dy = move_coords

        if game_map.is_cell_blocked(self.x + dx, self.y + dy):
            return

        self.__update_axis(True, self.x, dx)
        self.__update_axis(False, self.y, dy)

    def move_to_target(self, target_x, target_y, game_map, mobs):
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx ** 2 + dy ** 2)

        dx = int(dx / dist)
        dy = int(dy / dist)

        other = self.who_blocks(mobs, self.x + dx, self.y + dy)
        if not game_map.is_cell_blocked(self.x + dx, self.y + dy) and other is None:
            self.update_pos(self.x + dx, self.y + dy)

    def move_astar(self, target, game_map, mobs):
        if time.time() - self.stats.mv_time < self.stats.mv_wait:
            return

        self.stats.mv_time = time.time()

        fov = tc.map_new(game_map.wd, game_map.ht)
        for x in range(0, game_map.wd):
            for y in range(0, game_map.ht):
                tc.map_set_properties(fov, x, y, not game_map.cells[x][y].is_discovered,
                                      not game_map.cells[x][y].is_blocked)

        for mob in mobs:
            if mob != self and mob != target:
                tc.map_set_properties(fov, mob.x, mob.y, True, False)

        path = tc.path_new_using_map(fov, 0)
        tc.path_compute(path, self.x, self.y, target.x, target.y)
        if not tc.path_is_empty(path) and tc.path_size(path) < 30:
            x, y = tc.path_walk(path, True)
            if x or y:
                self.x = x
                self.y = y
            else:
                self.move_to_target(target.x, target.y, game_map, mobs)

            tc.path_delete(path)

    def act(self, target, fov_map, game_map, mobs):
        return self.strategy.act(self, target, fov_map, game_map, mobs)

    def get_dist(self, other):
        return np.linalg.norm(np.array([other.x, other.y]) - np.array([self.x, self.y]), ord=2)
