"""
    Mob реализация мобов.
"""

import random as rnd

from logic.entity import Entity
from logic.killer import kill_mob
from engine.engine_load_types import EngineLoadTypes
from logic.patterns.strategy import PassiveStrategy


class Mob(Entity):
    def __init__(self, item, *args, strategy=PassiveStrategy(),  load_type=EngineLoadTypes.NORMAL, **kwargs):
        super().__init__(*args, **kwargs)
        self.strategy = strategy
        self.start_pos_cnt_tries = 10
        if load_type == EngineLoadTypes.NORMAL:
            self.__init_start_pos()
        self.item = item
        if item:
            self.item.owner = self

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

    def serialize(self):
        data = {
            'x': self.x,
            'y': self.y,
            'scr_wd': self.sw,
            "scr_ht": self.sh,
            'ch': self.char,
            'clr': self.color,
            'name': self.name,
            'strat': self.strategy.__class__.__name__,
            'is_block': self.is_blocking,
            'render_ord': self.render_order.value,
            'main_clr': self.main_color,
            'stats': None,
            'item': None,
            'inventory': None
        }

        if self.item:
            data['item'] = self.item.serialize()
        if self.stats:
            data['stats'] = self.stats.serialize()

        return data

    def die(self):
        return kill_mob(self)

