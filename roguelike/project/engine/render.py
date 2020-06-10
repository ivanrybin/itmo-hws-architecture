import tcod as tc
from enum import Enum


class RenderOrder:
    DEAD_ENTITY = 1
    WORLD = 2
    ALIVE_ENTITY = 3


def draw_entity(cons, game_map, entity, fov_mode, fov_map):
    """
    Рисует сущности, попадающие в радиус FOV.
    """
    if fov_mode and not game_map.cells[entity.x][entity.y].is_discovered:
        # проверка видимости сущности
        if tc.map_is_in_fov(fov_map, entity.x, entity.y):
            # выбор цвета сущности
            tc.console_set_default_foreground(cons, entity.color)
            # вывод сущности на экран (номер консоли, координаты сущности, символ, фон)
            cons.put_char(entity.x, entity.y, entity.char, tc.BKGND_NONE)
    else:
        tc.console_set_default_foreground(cons, entity.color)
        cons.put_char(entity.x, entity.y, entity.char, tc.BKGND_NONE)


def clear_entity(cons, entity):
    cons.put_char(entity.x, entity.y, ord(' '), tc.BKGND_NONE)


def clear_all(cons, entities):
    for entity in entities:
        clear_entity(cons, entity)


# def render_bar(cons, bar, x, y, width, name, value, max_value):
#     curr_width = int(float(value) / max_value * width)
#
#     tc.console_set_default_background(cons, bar.back_color)
#     tc.console_rect(cons, x, y, width, 1, False, tc.BKGND_SCREEN)
#     tc.console_set_default_background(cons, bar.back_color)
#     if curr_width > 0:
#         tc.console_rect(cons, x, y, bar.wd, 1, False, tc.BKGND_SCREEN)
#
#     tc.console_set_default_foreground(cons, tc.white)
#     tc.console_print_ex(cons, int(x + width / 2), y, tc.BKGND_NONE,
#                         tc.CENTER, f'{bar.name}: {value}/{max_value}')


def render_all(cons, bars_cons, bars, player, game_map, entities, screen_width, screen_height, colors, fov_mode,
               fov_map):
    """
    Рисует карту и все объекты на ней, фиксиру  я текущий FOV.
    """
    for x in range(game_map.wd):
        for y in range(game_map.ht):
            is_visible = True
            if fov_mode:
                is_visible = tc.map_is_in_fov(fov_map, x, y)
            if is_visible or game_map.cells[x][y].is_discovered:
                if game_map.is_cell_blocked(x, y):
                    tc.console_set_char_background(cons, x, y, colors.get('main_wall'), tc.BKGND_SET)
                else:
                    tc.console_set_char_background(cons, x, y, colors.get('main_ground'), tc.BKGND_SET)
                game_map.cells[x][y].is_discovered = True
            elif not game_map.cells[x][y].is_discovered:
                if game_map.is_cell_blocked(x, y):
                    tc.console_set_char_background(cons, x, y, colors.get('fov_dark_walls'), tc.BKGND_SET)
                else:
                    tc.console_set_char_background(cons, x, y, colors.get('fov_dark_background'), tc.BKGND_SET)

    for entity in sorted(entities, key=lambda ent: ent.render_order):
        draw_entity(cons, game_map, entity, fov_mode, fov_map)

    cons.blit(cons, 0, 0, screen_width, screen_height, 0, 0, 0)

    tc.console_set_default_foreground(cons, tc.white)
    tc.console_print_ex(cons, 1, 1, tc.BKGND_NONE, tc.LEFT, 'HP: {0:02}/{1:02}'.format(player.stats.hp, player.stats.max_hp))

    # tc.console_set_default_background(bars_cons, tc.black)
    # tc.console_clear(bars_cons)
    #
    # for bar in bars:
    #     render_bar(bars_cons, bar, 1, 1, bar.wd, bar.name, player.stats.hp, player.stats.max_hp)
    #
    # tc.console_blit(bars_cons, 0, 0, screen_width, 7, 0, 0, screen_height - 7)