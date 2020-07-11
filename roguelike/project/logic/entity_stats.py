"""
    EntityStats реализует учет и обновление статистик игровых сущностей.
"""

import time
import tcod as tc

from logic.logger import Message, OperationLog
from logic.player import Player


class EntityStats:
    def __init__(self, hp, force, defense, owner=None):
        self.hp = hp
        self.max_hp = hp
        self.force = force
        self.defense = defense
        self.max_defense = defense
        self.owner = owner
        self.mv_time = time.time()
        self.mv_wait = 0.2
        self.armour = None

    def serialize(self):
        data = {
            'hp': self.hp,
            'max_hp': self.max_hp,
            'force': self.force,
            'defense': self.defense,
            'max_def': self.max_defense,
            'is_player': False,
            'armour': None,
        }
        if self.armour:
            data['is_player'] = True
            data['armour'] = self.armour.serialize()

        return data

    def increase_hp(self, delta):
        self.hp += delta
        if self.hp >= self.max_hp:
            self.hp = self.max_hp

    def decrease_hp(self, delta):
        operation_log = OperationLog()

        if self.armour and self.armour.item.defense > 0:
            self.armour.item.defense -= delta
            if self.armour.item.defense <= 0:
                delta = (-1) * self.armour.item.defense
                self.owner.color = self.owner.main_color
                self.max_defense -= self.armour.item.max_defense

                operation_log.add_item({'message': Message('Armour destroyed.', self.armour.item.color)})
                self.armour = None
            else:
                delta = 0

        if self.defense > 0:
            self.defense -= delta
            if self.defense < 0:
                delta = (-1) * self.defense
                self.defense = 0
            else:
                delta = 0

        self.hp -= delta

        if self.hp <= 0:
            operation_log.add_item({'dead': self.owner})

        return operation_log

    def attack_target(self, target):
        operation_log = OperationLog()

        if not target.stats:
            return operation_log

        damage = self.force

        if damage > 0:
            if isinstance(target, Player) or target.item is None:
                operation_log.add_item({'message': Message(f'{self.owner.name} damaged {target.name} in {damage} hps.',
                                                           tc.white)})
                operation_log.log.extend(target.stats.decrease_hp(damage).log)

        return operation_log
