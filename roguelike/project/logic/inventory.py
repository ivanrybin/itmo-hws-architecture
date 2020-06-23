import tcod as tc

from logic.logger import Message


class Item:
    def __init__(self):
        self.owner = None


class Inventory:
    def __init__(self, maxsize):
        self.items = []
        self.maxsize = maxsize
        self.owner = None

    def add_item(self, item):
        info = []

        if len(self.items) >= self.maxsize:
            info.append({'new_item': None,
                         'message': Message('Inventory is full.', tc.yellow)})
        else:
            info.append({'new_item': item,
                         'message': Message(f'New item {item.name}!', tc.light_azure)})
            self.items.append(item)

        return info

    def del_item(self, item):
        self.items.remove(item)

