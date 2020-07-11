"""
    Методы, уничтожающие сущности на карте.
"""

import tcod as tc

from logic.states import State
from logic.logger import Message
from logic.inventory import ItemType
from logic.logger import OperationLog
from engine.render import RenderOrder


def kill_player(player):
    player.char = ord('X')
    player.color = tc.darker_fuchsia

    return Message("You're DEAD. GAME OVER", tc.dark_red)


def kill_mob(mob):
    name = mob.name
    mob.char = ord('#')
    mob.color = tc.dark_grey
    mob.is_blocking = False
    mob.stats = None
    mob.act = lambda *args, **kwargs: OperationLog()
    mob.name = 'died ' + mob.name
    mob.render_order = RenderOrder.DEAD_ENTITY

    if mob.item is not None:
        if mob.item.type == ItemType.HP_PTN:
            mob.char = ord(' ')
            return Message('', tc.fuchsia), State.HEALTH_UP

        if mob.item.type == ItemType.INTOX_PTN:
            mob.char = ord(' ')
            return Message('', tc.fuchsia), State.INTOXICATE

    if name == 'Aggr':
        return Message(f'{name} is dead!', tc.yellow)

    return Message(f'{name} is dead!', tc.yellow)






