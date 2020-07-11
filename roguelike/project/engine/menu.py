"""
    Отрисовка меню.
"""

import tcod as tc


def menu(con, text, options, menu_width, screen_width, screen_height):
    header_height = tc.console_get_height_rect(con, 0, 0, menu_width, screen_height, text)
    height = len(options) + header_height
    window = tc.console_new(menu_width, height)
    tc.console_set_default_foreground(window, tc.white)
    tc.console_print_rect_ex(window, 0, 0, menu_width, height, tc.BKGND_NONE, tc.LEFT, text)

    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        tc.console_print_ex(window, 0, y, tc.BKGND_NONE, tc.LEFT, text)
        y += 1
        letter_index += 1

    x = int(screen_width / 2 - menu_width / 2)
    y = int(screen_height / 2 - height / 2)
    tc.console_blit(window, 0, 0, menu_width, height, 0, x, y, 1.0, 0.7)
    window.clear()


def inventory_menu(con, header, inventory, inventory_width, screen_width, screen_height):
    if len(inventory.items) == 0:
        options = ['Inventory is empty.']
    else:
        options = [item.name for item in inventory.items]

    menu(con, header, options, inventory_width, screen_width, screen_height)
