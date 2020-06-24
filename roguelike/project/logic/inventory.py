import tcod as tc

from logic.logger import Message
from logic.entity import EntityType


class Item:
    def __init__(self):
        pass


class Armour(Item):
    def __init__(self, defense=5, color=tc.dark_blue):
        self.defense = defense
        self.max_defense = defense
        self.color = color


class Sword(Item):
    def __init__(self, attack=5):
        self.attack = attack


class Inventory:
    def __init__(self, maxsize):
        self.items = []
        self.maxsize = maxsize
        self.owner = None

    def add_item(self, item_entity):
        info = []

        if len(self.items) >= self.maxsize:
            info.append({'new_item': None,
                         'message': Message('Inventory is full.', tc.yellow)})
        else:
            info.append({'new_item': item_entity,
                         'message': Message(f'New item {item_entity.name}!', tc.light_azure)})
            self.items.append(item_entity)

        return info

    def del_item(self, item_entity):
        self.items.remove(item_entity)

    def activate_item(self, item_entity):
        info = []

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
            info.append({'message': Message('Armour activated.', tc.yellow)})

            self.items.remove(item_entity)

        return info

    def drop_item(self, entities, item_entity):
        info = []

        item_entity.x = self.owner.x
        item_entity.y = self.owner.y
        entities.append(item_entity)

        self.del_item(item_entity)
        info.append({'message': Message(f'You dropped {item_entity.name}', tc.yellow)})

        return info


