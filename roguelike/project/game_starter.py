import os
from engine.engine import Engine
from engine.serialization import Serializer


def starter(default_screen=True, fov_mode=False, debug=False):
    scr_wd, scr_ht = 80, 40
    if not default_screen:
        scr_wd = int(input("Please, input the screen width:  "))
        scr_ht = int(input("Please, input the screen height: "))

    if os.path.isfile('media/GAME_SAVE.json'):
        new_or_save = str(input('Load save game - print 2, load SD-map - print 1, new game - 0: '))
        if new_or_save == '2':
            return Serializer.load_game('media/GAME_SAVE.json', is_save=True, scr_wd=scr_wd, scr_ht=scr_ht,
                                        fov_mode=fov_mode, debug=debug)
        elif new_or_save == '1':
            return Serializer.load_game('media/SD_MAP.json', is_save=False, scr_wd=scr_wd, scr_ht=scr_ht,
                                        fov_mode=fov_mode, debug=debug)

        return Engine(screen_width=scr_wd, screen_height=scr_ht, fov_mode=fov_mode, debug=debug)

    new_or_load = str(input('Load SD-map - print 1, new game - 0: '))
    if new_or_load == '1':
        return Serializer.load_game('media/SD_MAP.json',
                                    is_save=False,
                                    scr_wd=scr_wd,
                                    scr_ht=scr_ht,
                                    fov_mode=fov_mode,
                                    debug=debug)

    return Engine(screen_width=scr_wd, screen_height=scr_ht, fov_mode=fov_mode, debug=debug)
