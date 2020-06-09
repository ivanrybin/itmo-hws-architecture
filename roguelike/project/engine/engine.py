import tcod as tc
import random as rnd

import engine.render as rr
# logic
from logic.player import Player
from logic.random_mob import RandomMob
from map.game_map import Map
from map.wall import Wall
from map.room import Room


def to_int(value):
    return int(value)


colors = {'dark_wall': tc.Color(0, 0, 100),
          'dark_ground': tc.Color(50, 50, 150),
          'brown_wall': tc.Color(167, 103, 65),
          'normal_ground': tc.Color(0, 30, 30),
          'kate_ground': tc.Color(200, 146, 7)}


class Engine:
    def __init__(self, screen_width=80, screen_height=40, dungeon=False, debug=False):
        self.scr_wd = to_int(screen_width)
        self.scr_ht = to_int(screen_height)
        self.player_init_x = to_int(screen_width * 0.03)
        self.player_init_y = to_int(screen_height * 0.07)
        # инициализация среды
        self.dungeon = dungeon
        self.map = self.__init_map()
        self.player = self.__init_player()
        self.entities = [self.player, *self.__init_mobs()]
        self.fov = self.__init_fov()
        self.fov_radius = 15
        # служебные штуки
        self.DEBUG = debug
        self.FONT_PATH = 'media/arial10x10.png'
        self.GAME_NAME = 'RogueLike SD - Ivan Rybin, ITMO JB SE'

    def __init_map(self):
        game_map = Map(self.scr_wd, self.scr_ht,
                       self.player_init_x, self.player_init_y, self.dungeon)
        if self.dungeon:
            game_map.create_rooms()
        else:
            game_map.create_walls()
        return game_map

    def __init_player(self):
        player = Player(self.player_init_x, self.player_init_y,
                        screen_width=self.scr_wd, screen_height=self.scr_ht,
                        char="@", color=tc.white)
        return player

    def __init_mobs(self, cnt=rnd.randint(5, 20)):
        mobs = []
        chars = [197, 185, 180, 206, 205, 178]
        colors = [tc.darker_green, tc.dark_flame, tc.dark_azure, tc.gold, tc.gray,
                  tc.green, tc.black, tc.blue, tc.dark_orange, tc.dark_cyan]
        for i in range(0, cnt):
            char = chars[rnd.randint(0, len(chars) - 1)]
            color = colors[rnd.randint(0, len(colors) - 1)]
            mob = RandomMob(None, None,
                            screen_width=self.scr_wd, screen_height=self.scr_ht,
                            char="#", color=color, game_map=self.map)
            mob.char = char
            mobs.append(mob)

        return mobs

    def __init_fov(self):
        fov_map = tc.map_new(self.map.wd, self.map.ht)
        for x in range(self.map.wd):
            for y in range(self.map.ht):
                tc.map_set_properties(fov_map, x, y,
                                      not self.map.cells[x][y].is_walk,
                                      not self.map.cells[x][y].is_blocked)
        return fov_map

    def recompute_fov(self, x, y, radius, light_walls=True, algorithm=0):
        tc.map_compute_fov(self.fov, x, y, radius, light_walls, algorithm)

    def load_map(self):
        pass

    def keys_handler(self):
        for event in tc.event.get():
            # debug
            if self.DEBUG:
                if event.type != "MOUSEMOTION":
                    print(event)
            # quit
            if event.type == "QUIT":
                raise SystemExit()
            # нажатие клавивиши
            if event.type == "KEYDOWN":
                if event.sym == tc.event.K_ESCAPE:
                    raise SystemExit()
                if event.sym in [tc.event.K_UP, tc.event.K_DOWN, tc.event.K_LEFT, tc.event.K_RIGHT]:
                    if event.sym == tc.event.K_UP:
                        self.player.move("UP", self.map)
                    if event.sym == tc.event.K_DOWN:
                        self.player.move("DOWN", self.map)
                    if event.sym == tc.event.K_LEFT:
                        self.player.move("LEFT", self.map)
                    if event.sym == tc.event.K_RIGHT:
                        self.player.move("RIGHT", self.map)

    def run(self):
        fov_recompute = True
        # подгрузка шрифта
        tc.console_set_custom_font(self.FONT_PATH, tc.FONT_TYPE_GREYSCALE | tc.FONT_LAYOUT_TCOD)
        # инициализация главной консоли
        with tc.console_init_root(self.scr_wd, self.scr_ht, title=self.GAME_NAME, fullscreen=False) as root_console:
            while True:
                self.recompute_fov(self.player.x, self.player.y, self.fov_radius)
                # отрисовка сущностей
                rr.render_all(root_console, self.map, self.entities, self.scr_wd, self.scr_ht, colors, self.fov)
                # вывод консоли
                tc.console_flush()
                # удаление предыдущих позиций
                rr.clear_all(root_console, self.entities)
                # получени ввода пользователя
                self.keys_handler()


def starter(default=False, dungeon=False, debug=False):
    if default:
        return Engine(debug=debug)

    # h = to_int(input("Please, input the screen height: "))
    # w = to_int(input("Please, input the screen width:  "))
    return Engine(dungeon=dungeon, debug=debug)
