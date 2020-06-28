"""
    Inventory реализует инвентарь игрока.
"""

import tcod as tc
from logic.logger import Message, OperationLog
from logic.entity import EntityType
from enum import Enum


class ItemType(Enum):
    ARMOUR_I = 1
    ARMOUR_II = 2
    HP_PTN = 3
    INTOX_PTN = 4


class Item:
    def __init__(self, color, type):
        self.color = color
        self.type = type


class Armour(Item):
    def __init__(self, defense=5, color=tc.dark_blue, arm_type=ItemType.ARMOUR_I):
        super().__init__(color, arm_type)
        self.defense = defense
        self.max_defense = defense

    def serialize(self):
        data = {
            'defense': self.defense,
            'max_def': self.max_defense,
            'clr': self.color,
            'type': self.type.value
        }
        return data


class HealthPotion(Item):
    def __init__(self, health_up=5, color=tc.light_sea):
        super().__init__(color, ItemType.HP_PTN)
        self.hp_up = health_up

    def serialize(self):
        data = {
            'hp_up': self.hp_up,
            'clr': self.color,
            'type': self.type.value
        }
        return data


class IntoxPotion(Item):
    def __init__(self, intox_time=5, color=tc.light_violet):
        super().__init__(color, ItemType.INTOX_PTN)
        self.intox_time = intox_time

    def serialize(self):
        data = {
            'intox_time': self.intox_time,
            'clr': self.color,
            'type': self.type.value
        }
        return data


class Inventory:
    def __init__(self, maxsize):
        self.items = []
        self.maxsize = maxsize
        self.owner = None

    def serialize(self):
        data = {
            'maxsize': self.maxsize,
            'items': [item.serialize() for item in self.items]
        }
        return data

    def add_item(self, item_entity):
        operation_log = OperationLog()

        if len(self.items) >= self.maxsize:
            operation_log.add_item({'new_item': None,
                                    'message': Message('Inventory is full.', tc.yellow)})
        else:
            operation_log.add_item({'new_item': item_entity,
                                    'message': Message(f'New item {item_entity.name}!', tc.light_azure)})
            self.items.append(item_entity)

        return operation_log

    def del_item(self, item_entity):
        self.items.remove(item_entity)

    def activate_item(self, item_entity):
        operation_log = OperationLog()

        if item_entity.type == EntityType.ARMOUR:
            if self.owner.stats.armour:
                self.items.append(self.owner.stats.armour)
                self.owner.stats.max_defense -= self.owner.stats.armour.item.max_defense
                self.owner.color = self.owner.main_color
                self.owner.stats.armour = None

            self.owner.stats.armour = item_entity
            self.owner.main_color = self.owner.color
            self.owner.color = item_entity.item.color
            self.owner.stats.max_defense += item_entity.item.max_defense
            operation_log.add_item({'message': Message('Armour activated.', tc.yellow)})

            self.items.remove(item_entity)

        return operation_log

    def drop_item(self, entities, item_entity):
        operation_log = OperationLog()

        item_entity.x = self.owner.x
        item_entity.y = self.owner.y
        entities.append(item_entity)

        self.del_item(item_entity)
        operation_log.add_item({'message': Message(f'You dropped {item_entity.name}', tc.yellow)})

        return operation_log
