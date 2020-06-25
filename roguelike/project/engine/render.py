"""
    Блок отвечающий за отрисовку всех объектов игры.
"""

import tcod as tc

from logic.states import State
from engine.menu import inventory_menu


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


def render_bar(panel, x, y, total_width, name, value, maximum, bar_color, back_color):
    bar_width = int(float(value) / maximum * total_width)

    tc.console_set_default_background(panel, back_color)
    tc.console_rect(panel, x, y, total_width, 1, False, tc.BKGND_SCREEN)

    tc.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        tc.console_rect(panel, x, y, bar_width, 1, False, tc.BKGND_SCREEN)

    tc.console_set_default_foreground(panel, tc.white)
    tc.console_print_ex(panel, int(x + total_width / 2), y, tc.BKGND_NONE, tc.CENTER, '{0}: {1}/{2}'.format(name, value, maximum))


def render_all(cons, bars_cons, player, game_map, entities, screen_width, screen_height, colors, fov_mode,
               fov_map, msg_log):
    """
    Рисует карту и все объекты на ней, фиксируя текущий FOV.
    """
    cons.clear()
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

    # bars
    tc.console_set_default_background(bars_cons, tc.black)
    tc.console_clear(bars_cons)

    # print msgs
    y = 2
    for msg in msg_log.msgs:
        tc.console_set_default_foreground(bars_cons, msg.color)
        tc.console_print_ex(bars_cons, msg_log.x, y, tc.BKGND_NONE, tc.LEFT, msg.txt)
        y += 1

    # рендер панели здоровья
    # cons, x, y, width, name, curr_stat, total_stat, forground, background
    render_bar(bars_cons, 0, 0, 26, 'HP', player.stats.hp, player.stats.max_hp,
               tc.light_red, tc.darker_red)
    defense = player.stats.defense
    if player.stats.armour:
        defense += player.stats.armour.item.defense

    render_bar(bars_cons, 0, 1, 26, 'DEFENSE', defense, player.stats.max_defense,
               tc.light_blue, tc.dark_blue)

    # bars_cons, x, y, ширина панели, высота панели, консоль, смещение по x, смещение по y
    tc.console_blit(bars_cons, 0, 0, 26, 5, cons, 0, 0)

    # отрисовка меню
    if game_map.state == State.SHOWING_MENU:
        inventory_menu(cons, 'Choose item via 1,2,3 and/or press Esc to quit.\n',
                       player.inventory, 50, screen_width, screen_height)
    elif game_map.state == State.DROP_ITEM:
        inventory_menu(cons, 'Drop item via 1,2,3 and/or press Esc to quit.\n',
                       player.inventory, 50, screen_width, screen_height)
