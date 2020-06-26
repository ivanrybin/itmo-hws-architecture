"""
    Mob реализация мобов.
"""

import random as rnd
from logic.entity import Entity


class Mob(Entity):
    def __init__(self, *args, load_type='NORMAL', **kwargs):
        super().__init__(*args, **kwargs)
        self.start_pos_cnt_tries = 10
        if load_type == 'NORMAL':
            self.__init_start_pos()

    def __init_start_pos(self):
        for i in range(0, self.start_pos_cnt_tries):
            self.x = rnd.randint(int(self.map.wd * 0.15), int(self.map.wd * 0.98))
            self.y = rnd.randint(int(self.map.ht * 0.15), int(self.map.ht * 0.98))
            not_in_wall_respawn = True
            for wall in self.map.walls:
                if wall.is_point_in(self.x, self.y):
                    not_in_wall_respawn = False

            if not_in_wall_respawn:
                break
