import tcod as tc
from logic.entity import Entity


class Player(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mv_types = {'LEFT': (-1, 0), 'RIGHT': (1, 0),
                         'UP': (0, -1), 'DOWN': (0, 1)}

    def move(self, move, game_map):
        dx, dy = self.mv_types[move]

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

        print(self.x, self.y)
