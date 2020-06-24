import time
import tcod as tc

from logic.logger import Message
from logic.entity import EntityType


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
        self.intox_start_time = None
        self.armour = None

    def increase_hp(self, delta):
        self.hp += delta
        if self.hp >= self.max_hp:
            self.hp = self.max_hp

    def decrease_hp(self, delta):
        info = []
        if self.armour and self.armour.item.defense > 0:
            self.armour.item.defense -= delta
            if self.armour.item.defense <= 0:
                delta = (-1) * self.armour.item.defense
                self.owner.color = self.owner.main_color
                self.max_defense -= self.armour.item.max_defense

                info.append({'message': Message('Armour destroyed.', self.armour.item.color)})
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
            info.append({'dead': self.owner})

        return info

    def attack_target(self, target):
        info = []
        if not target.stats:
            return info

        damage = self.force

        if damage > 0:
            if target.type not in [EntityType.HEALTH_PTN, EntityType.INTOX_PTN]:
                info.append({'message': Message(f'{self.owner.name} damaged {target.name} in {damage} hps.',
                                                tc.white)})
                info.extend(target.stats.decrease_hp(damage))
        return info
