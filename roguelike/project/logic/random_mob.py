import tcod as tc
import time
import random as rnd
from logic.entity import Entity


class RandomMob(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mv_time = time.time()
        self.__init_start_pos()
        self.mv_wait = rnd.randint(1, 3)

    def __init_start_pos(self):
        if self.map.dungeon:
            room = self.map.rooms[rnd.randint(1, len(self.map.rooms) - 1)]
            self.x, self.y = rnd.randint(room.x1 + 1, room.x2 - 2), rnd.randint(room.y1 + 1, room.y2 - 2)
        else:
            for i in range(0, 5):
                self.x = rnd.randint(int(self.map.wd * 0.1), int(self.map.wd * 0.98))
                self.y = rnd.randint(int(self.map.ht * 0.1), int(self.map.ht * 0.98))
                is_ok = True
                for wall in self.map.walls:
                    if wall.is_point_in(self.x, self.y):
                        is_ok = False

                if is_ok:
                    break

    def update_pos(self, game_map):
        if time.time() - self.mv_time < self.mv_wait:
            return

        self.mv_time = time.time()

        dx = rnd.randint(-1, 1)
        dy = 0
        if dx == 0:
            dy = rnd.randint(-1, 1)

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
