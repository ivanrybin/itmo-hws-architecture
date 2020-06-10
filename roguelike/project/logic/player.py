import tcod as tc
from logic.entity import Entity, who_blockes
from logic.states import State


class Player(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mv_types = {'LEFT': (-1, 0), 'RIGHT': (1, 0),
                         'UP': (0, -1), 'DOWN': (0, 1)}

    def move(self, move, game_map, mobs):

        if game_map.state != State.PLAYER_TURN:
            return []

        dx, dy = self.mv_types[move]

        if game_map.is_cell_blocked(self.x + dx, self.y + dy):
            return []

        victim = who_blockes(self, mobs[1:], self.x + dx, self.y + dy)

        if victim:
            return self.stats.attack_target(victim)
        else:
            self.update_pos(dx, dy, game_map)

        game_map.state = State.MOB_TURN

        print(self.x, self.y)

        return []


