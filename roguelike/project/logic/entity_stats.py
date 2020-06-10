import time
import random as rnd


class EntityStats:
    def __init__(self, hp, force, defense, owner=None):
        self.hp = hp
        self.max_hp = hp
        self.force = force
        self.defense = defense
        self.owner = owner
        self.mv_time = time.time()
        self.mv_wait = 0.2

    def decrease_hp(self, delta):
        info = []

        self.hp -= delta

        if self.hp <= 0:
            info.append({'dead': self.owner})

        return info

    def attack_target(self, target):
        info = []
        if not target.stats:
            return info

        damage = self.force - target.stats.defense

        if damage > 0:
            info.append({'message': f'{self.owner.name} атаковал {target.name} на {damage} урона.'})
            info.extend(target.stats.decrease_hp(damage))

        return info
