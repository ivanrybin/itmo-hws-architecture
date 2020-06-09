import tcod as tc


def draw_entity(con, fov_map, game_map, entity):
    """
    Рисует сущность.
    """
    if tc.map_is_in_fov(fov_map, entity.x, entity.y):
        entity.update_pos(game_map)
        # выбор цвета сущности
        tc.console_set_default_foreground(con, entity.color)
        # вывод сущности на экран (номер консоли, координаты сущности, символ, фон)
        con.put_char(entity.x, entity.y, entity.char, tc.BKGND_NONE)


def clear_entity(con, entity):
    con.put_char(entity.x, entity.y, ord(' '), tc.BKGND_NONE)


def clear_all(con, entities):
    for entity in entities:
        clear_entity(con, entity)


def render_all(con, game_map, entities, screen_width, screen_height, colors, fov_map):
    """
    Рисует все сущности и стены
    """
    for y in range(game_map.ht):
        for x in range(game_map.wd):
            is_visible = tc.map_is_in_fov(fov_map, x, y)
            if is_visible:
                if game_map.is_cell_blocked(x, y):
                    tc.console_set_char_background(con, x, y, colors.get('brown_wall'), tc.BKGND_SET)
                else:
                    tc.console_set_char_background(con, x, y, colors.get('normal_ground'), tc.BKGND_SET)
            else:
                if game_map.is_cell_blocked(x, y):
                    tc.console_set_char_background(con, x, y, colors.get('dark_wall'), tc.BKGND_SET)
                else:
                    tc.console_set_char_background(con, x, y, colors.get('dark_ground'), tc.BKGND_SET)


    for entity in entities:
        draw_entity(con, fov_map, game_map, entity)

    # пока непонятно, что это делает
    con.blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)