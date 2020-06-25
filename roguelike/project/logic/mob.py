"""
    Mob реализация мобов.
"""

import random as rnd
from logic.entity import Entity


class Mob(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__init_start_pos()

    def __init_start_pos(self):
        if self.map.dungeon:
            room = self.map.rooms[rnd.randint(1, len(self.map.rooms) - 1)]
            self.x, self.y = rnd.randint(room.x1 + 1, room.x2 - 2), rnd.randint(room.y1 + 1, room.y2 - 2)
        else:
            for i in range(0, 5):
                self.x = rnd.randint(int(self.map.wd * 0.15), int(self.map.wd * 0.98))
                self.y = rnd.randint(int(self.map.ht * 0.15), int(self.map.ht * 0.98))
                not_in_wall_respawn = True
                for wall in self.map.walls:
                    if wall.is_point_in(self.x, self.y):
                        not_in_wall_respawn = False

                if not_in_wall_respawn:
                    break
