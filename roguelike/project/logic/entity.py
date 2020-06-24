import tcod as tc
import numpy as np
import math
import time
from enum import Enum

from engine.render import RenderOrder

def who_blockes(self, mobs, dest_x, dest_y):
    for mob in mobs:
        if mob != self and mob.x == dest_x and mob.y == dest_y and mob.stats and mob.is_blocking:
            return mob
    return None


class EntityType(Enum):
    PLAYER = 1
    MOB = 2
    ITEM = 3
    HEALTH_PTN = 4
    INTOX_PTN = 5
    ARMOUR = 6


class Entity:
    def __init__(self, x, y, screen_width, screen_height, char, color, name,
                 stats=None, game_map=None, strategy=None,
                 is_blocking=True, render_order=RenderOrder.ALIVE_ENTITY,
                 item=None, inventory=None, entity_type=None):
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

        if self.item:
            self.item.owner = self
        if self.inventory:
            self.inventory.owner = self

    def update_pos(self, dx, dy, game_map):
        if game_map.is_cell_blocked(self.x + dx, self.y + dy):
            return

        if 0 <= self.x + dx < self.sw:
            self.x += dx
        elif self.x + dx >= self.sw:
            self.x = self.sw - 1
        elif self.x + dx < 0:
            self.x = 0

        if 0 <= self.y + dy < self.sh:
            self.y += dy
        elif self.y + dy >= self.sh:
            self.y = self.sh - 1
        elif self.y + dy < 0:
            self.y = 0

    def move_to_target(self, target_x, target_y, game_map, mobs):
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx ** 2 + dy ** 2)

        dx = int(dx / dist)
        dy = int(dy / dist)

        other = who_blockes(self, mobs, self.x + dx, self.y + dy)
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
