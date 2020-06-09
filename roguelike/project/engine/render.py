import tcod as tc


def draw_entity(con, game_map, entity, fov_mode, fov_map):
    """
    Рисует сущности, попадающие в радиус FOV.
    """
    if fov_mode and not game_map.cells[entity.x][entity.y].is_discovered:
        # проверка видимости сущности
        if tc.map_is_in_fov(fov_map, entity.x, entity.y):
            # обновление позиции сущности, если она бот
            entity.update_pos(game_map)
            # выбор цвета сущности
            tc.console_set_default_foreground(con, entity.color)
            # вывод сущности на экран (номер консоли, координаты сущности, символ, фон)
            con.put_char(entity.x, entity.y, entity.char, tc.BKGND_NONE)
    else:
        entity.update_pos(game_map)
        tc.console_set_default_foreground(con, entity.color)
        con.put_char(entity.x, entity.y, entity.char, tc.BKGND_NONE)


def clear_entity(con, entity):
    con.put_char(entity.x, entity.y, ord(' '), tc.BKGND_NONE)


def clear_all(con, entities):
    for entity in entities:
        clear_entity(con, entity)


def render_all(con, game_map, entities, screen_width, screen_height, colors, fov_mode, fov_map):
    """
    Рисует карту и все объекты на ней, фиксируя текущий FOV.
    """
    for x in range(game_map.wd):
        for y in range(game_map.ht):
            is_visible = True
            if fov_mode:
                is_visible = tc.map_is_in_fov(fov_map, x, y)
            if is_visible or game_map.cells[x][y].is_discovered:
                if game_map.is_cell_blocked(x, y):
                    tc.console_set_char_background(con, x, y, colors.get('main_wall'), tc.BKGND_SET)
                else:
                    tc.console_set_char_background(con, x, y, colors.get('main_ground'), tc.BKGND_SET)
                game_map.cells[x][y].is_discovered = True
            elif not game_map.cells[x][y].is_discovered:
                if game_map.is_cell_blocked(x, y):
                    tc.console_set_char_background(con, x, y, colors.get('fov_dark_walls'), tc.BKGND_SET)
                else:
                    tc.console_set_char_background(con, x, y, colors.get('fov_dark_background'), tc.BKGND_SET)

    for entity in entities:
        draw_entity(con, game_map, entity, fov_mode, fov_map)

    con.blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)