import tcod as tc
from logic.entity import *
from logic.states import State
from logic.decorator import intoxicating_deco


class Player(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mv_types = {'LEFT': (-1, 0), 'RIGHT': (1, 0),
                         'UP': (0, -1), 'DOWN': (0, 1)}

    def apply_item(self, item):
        info = []

        if item.type == EntityType.HEALTH_PTN:
            info.append({'message': Message('+5 HP potion!', tc.green)})
            self.stats.increase_hp(5)
            self.inventory.del_item(item)

        elif item.type == EntityType.INTOX_PTN:
            info.append({'message': Message('You\'re intoxicated', tc.fuchsia)})
            if self.stats.intox_start_time:
                self.stats.intox_start_time += 7
            else:
                self.stats.intox_start_time = time.time()

            self.inventory.del_item(item)
            intoxicating_deco(self)


        return info

    def get_item(self, game_map, entities):
        info = []
        for entity in entities:
            if entity.x == self.x and entity.y == self.y and \
                    entity.type in [EntityType.HEALTH_PTN, EntityType.INTOX_PTN]:
                info = self.inventory.add_item(entity)
                break

        return info

    @staticmethod
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
