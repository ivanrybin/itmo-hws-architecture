"""
    Player реализация сущности игрока.
"""
import time
import tcod as tc

from logic.entity import Entity
from logic.inventory import ItemType
from logic.logger import Message
from logic.logger import OperationLog
from logic.killer import kill_player
from logic.mob import Mob


class Player(Entity):
    def __init__(self, inventory, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inventory = inventory
        self.inventory.owner = self

    def pick_item(self, item):
        operation_log = OperationLog()

        if item.item.type == ItemType.HP_PTN:
            operation_log.add_item({'message': Message(f'+{item.item.hp_up} HP potion!', tc.green)})
            self.stats.increase_hp(5)
            self.inventory.del_item(item)

        elif item.item.type == ItemType.INTOX_PTN:
            operation_log.add_item({'message': Message('You\'re intoxicated!', tc.fuchsia)})
            if self.mv_handler.intox_start_time:
                self.mv_handler.intox_start_time += item.item.intox_time
            else:
                self.mv_handler.set_intox_start_time(time.time())

            self.inventory.del_item(item)

        return operation_log

    def get_item(self, entities):
        operation_log = OperationLog()

        for entity in entities:
            if entity.x == self.x and entity.y == self.y:
                if isinstance(entity, Mob) and entity.item is not None:
                    operation_log = OperationLog()
                    if not self.inventory.add_item(entity):
                        operation_log.add_item({'new_item': None,
                                                'message': Message('Inventory is full.', tc.yellow)})
                    else:
                        operation_log.add_item({'new_item': entity,
                                                'message': Message(f'New item {entity.name}!', tc.light_azure)})
                    break

        return operation_log

    def serialize(self):
        data = {
            'x': self.x,
            'y': self.y,
            'scr_wd': self.sw,
            "scr_ht": self.sh,
            'ch': self.char,
            'clr': self.color,
            'name': self.name,
            'is_block': self.is_blocking,
            'render_ord': self.render_order.value,
            'main_clr': self.main_color,
            'stats': None,
            'item': None,
            'inventory': self.inventory.serialize(),
        }

        if self.stats:
            data['stats'] = self.stats.serialize()

        return data

    def die(self):
        return kill_player(self)
