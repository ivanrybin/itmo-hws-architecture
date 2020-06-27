"""
    Player реализация сущности игрока.
"""
import time
import tcod as tc

from logic.entity import Entity, EntityType
from logic.logger import Message
from logic.logger import OperationLog


class Player(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def pick_item(self, item):
        operation_log = OperationLog()

        if item.type == EntityType.HEALTH_PTN:
            operation_log.add_item({'message': Message(f'+{item.item.hp_up} HP potion!', tc.green)})
            self.stats.increase_hp(5)
            self.inventory.del_item(item)

        elif item.type == EntityType.INTOX_PTN:
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
            if entity.x == self.x and entity.y == self.y and \
                    entity.type in [EntityType.HEALTH_PTN, EntityType.INTOX_PTN, EntityType.ARMOUR]:
                operation_log = self.inventory.add_item(entity)
                break

        return operation_log
