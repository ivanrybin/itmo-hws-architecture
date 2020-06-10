import tcod as tc

from logic.states import State
from engine.render import RenderOrder


def kill_player(player):
    player.char = 'X'
    player.color = tc.darker_fuchsia

    return "You're DEAD. GAME OVER", State.PLAYER_DEAD


def kill_mob(mob):
    name = mob.name

    mob.char = ord('#')
    mob.color = tc.dark_grey
    mob.is_blocking = False
    mob.stats = None
    mob.act = lambda *args, **kwargs: None
    mob.name = 'died ' + mob.name
    mob.render_order = RenderOrder.DEAD_ENTITY

    return [f'{name} is dead!']
