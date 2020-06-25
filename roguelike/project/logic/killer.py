"""
    Методы, уничтожающие сущности на карте.
"""

import tcod as tc

from logic.states import State
from logic.logger import Message
from logic.entity import EntityType

from engine.render import RenderOrder


def kill_player(player):
    player.char = ord('X')
    player.color = tc.darker_fuchsia

    return Message("You're DEAD. GAME OVER", tc.dark_red), State.PLAYER_DEAD


def kill_mob(mob):
    name = mob.name

    mob.char = ord('#')
    mob.color = tc.dark_grey
    mob.is_blocking = False
    mob.stats = None
    mob.act = lambda *args, **kwargs: None
    mob.name = 'died ' + mob.name
    mob.render_order = RenderOrder.DEAD_ENTITY

    if mob.type == EntityType.HEALTH_PTN:
        mob.char = ord(' ')
        return Message('', tc.fuchsia), State.HEALTH_UP

    if name == EntityType.INTOX_PTN:
        mob.char = ord(' ')
        return Message('', tc.fuchsia), State.INTOXICATE

    if name == 'Aggr':
        return True, Message(f'{name} is dead!', tc.yellow), State.PLAYER_TURN

    return False, Message(f'{name} is dead!', tc.yellow), State.PLAYER_TURN
