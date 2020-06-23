import tcod as tc
import random as rnd

# render
import engine.render as rr
from engine.bar import Bar

# logic
from logic.player import Player
from logic.mob import Mob
from logic.strategy import *
from logic.states import State
from logic.entity import EntityType
from logic.entity_stats import EntityStats
from logic.killer import kill_player, kill_mob
from logic.logger import MessageLog
from logic.inventory import *

# map
from map.game_map import Map
from map.wall import Wall
from map.room import Room


def to_int(value):
    return int(value)


colors = {'fov_dark_walls': tc.Color(0, 5, 90),
          'fov_dark_background': tc.Color(45, 45, 140),
          'main_wall': tc.Color(167, 103, 65),
          'main_ground': tc.Color(0, 30, 30),
          'kate_ground': tc.Color(200, 146, 7)}


class Engine:
    def __init__(self, screen_width=80, screen_height=40, dungeon=False, fov_mode=False, debug=False):
        self.scr_wd = to_int(screen_width)
        self.scr_ht = to_int(screen_height)
        self.player_init_x = to_int(screen_width * 0.03)
        self.player_init_y = to_int(screen_height * 0.13)
        # инициализация среды
        self.dungeon = dungeon
        self.map = self.__init_map()
        self.player = self.__init_player()
        self.entities = [self.player, *self.__init_mobs()]
        self.fov = None
        if fov_mode:
            self.fov = self.__init_fov()
            self.fov_radius = 15
        self.whoes_state = State.PLAYER_TURN
        # служебные штуки
        self.msg_log = MessageLog(0, 26, 3)
        self.bars = [Bar(20, 7, screen_height - 7, 'HP', tc.light_red)]
        self.BARS_CONS = tc.console_new(self.scr_wd, self.scr_ht)
        self.FOV_MODE = fov_mode
        self.DEBUG = debug
        self.FONT_PATH = 'media/arial10x10.png'
        self.GAME_NAME = 'RogueLike SD - Ivan Rybin, Elizaveta Sidorova, ITMO JB SD SE'

    def __init_map(self):
        game_map = Map(self.scr_wd, self.scr_ht,
                       self.player_init_x, self.player_init_y,
                       self.dungeon)
        if self.dungeon:
            game_map.create_rooms()
        else:
            game_map.create_walls()
        return game_map

    def __init_player(self):
        stats = EntityStats(hp=30, force=4, defense=2)
        player = Player(self.player_init_x, self.player_init_y,
                        screen_width=self.scr_wd, screen_height=self.scr_ht,
                        char=203, color=tc.white, name='Bob', stats=stats,
                        inventory=Inventory(3),
                        entity_type=EntityType.PLAYER)
        player.stats.owner = player

        return player

    def __init_mobs(self, cnt=rnd.randint(5, 20)):
        chars = [197, 185, 180, 206, 205, 178]
        colors = [tc.darker_green, tc.dark_flame, tc.dark_azure, tc.gold, tc.gray,
                  tc.green, tc.black, tc.blue, tc.dark_orange, tc.dark_cyan]

        mobs = []
        # вероятности появления пугливых, пассивных, агрессивных
        mob_probs = {(0, 0.2): 'coward',
                     (0.2, 0.7): 'passive',
                     (0.7, 1): 'aggressive'}
        # символ, цвет, стратегия моба
        mob_types = {'passive': (205, tc.dark_green, 'Cow', PassiveStrategy),
                     'aggressive': (206, tc.dark_flame, 'Aggr', AggressiveStrategy),
                     'coward': (197, tc.light_cyan, 'Aaaa', CowardStrategy)}
        # характеристика мобов: здоровье, сила, защита
        mob_stats = {'passive': (20, 0, 1),
                     'aggressive': (15, 4, 2),
                     'coward': (5, 0, 1)}
        # случайны выбор типа моба
        for i in range(0, cnt):
            prob = rnd.random()
            for l, r in mob_probs.keys():
                if l < prob < r:
                    mob_type = mob_probs[(l, r)]
                    mob_char, mob_colr, mob_name, mob_strat = mob_types[mob_type]
                    mob_stat = mob_stats[mob_type]
                    mob = Mob(None, None,
                              screen_width=self.scr_wd, screen_height=self.scr_ht,
                              char=mob_char, color=mob_colr,
                              name=mob_name, stats=EntityStats(*mob_stat),
                              game_map=self.map, strategy=mob_strat,
                              entity_type=EntityType.MOB)
                    mob.stats.owner = mob
                    mobs.append(mob)

        # генерация зелий
        potions = []
        potions_probs = {(0, 0.2): 'healing',
                         (0.2, 0.4): 'intoxicating'}

        potions_types = {'healing': (24, tc.light_sea, 'healing potion', PassiveStrategy, EntityType.HEALTH_PTN),
                         'intoxicating': (25, tc.light_violet, 'intoxicating potion', PassiveStrategy, EntityType.INTOX_PTN)}

        potions_stats = {'healing': (0, 0, 0),
                         'intoxicating': (0, 0, 0)}

        for i in range(0, 10):
            prob = rnd.random()
            for l, r in potions_probs.keys():
                if l <= prob <= r:
                    ptn_type = potions_probs[(l, r)]
                    ptn_char, ptn_colr, ptn_name, ptn_strat, ptn_real_type = potions_types[ptn_type]
                    ptn_stat = potions_stats[ptn_type]
                    ptn = Mob(None, None,
                              screen_width=self.scr_wd, screen_height=self.scr_ht,
                              char=ptn_char, color=ptn_colr,
                              name=ptn_name, stats=EntityStats(*ptn_stat),
                              game_map=self.map, strategy=ptn_strat,
                              item=Item(), is_blocking=False,
                              entity_type=ptn_real_type)
                    ptn.stats.owner = ptn
                    potions.append(ptn)

        return mobs + potions

    def __init_fov(self):
        fov_map = tc.map_new(self.map.wd, self.map.ht)
        for x in range(self.map.wd):
            for y in range(self.map.ht):
                tc.map_set_properties(fov_map, x, y,
                                      not self.map.cells[x][y].is_discovered,
                                      not self.map.cells[x][y].is_blocked)
        return fov_map

    def __recompute_fov(self, x, y, radius, light_walls=True, algorithm=0):
        tc.map_compute_fov(self.fov, x, y, radius, light_walls, algorithm)

    def load_map(self):
        pass

    def __keys_handler(self):
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
                if event.sym in [tc.event.K_UP, tc.event.K_DOWN, tc.event.K_LEFT, tc.event.K_RIGHT, tc.event.K_g]:
                    if event.sym == tc.event.K_UP:
                        return self.player.move(self.player, "UP", self.map, self.entities)
                    if event.sym == tc.event.K_DOWN:
                        return self.player.move(self.player, "DOWN", self.map, self.entities)
                    if event.sym == tc.event.K_LEFT:
                        return self.player.move(self.player, "LEFT", self.map, self.entities)
                    if event.sym == tc.event.K_RIGHT:
                        return self.player.move(self.player, "RIGHT", self.map, self.entities)
                    if event.sym == tc.event.K_g:
                        return self.player.get_item(self.map, self.entities)
                    # if event.sym == tc.event.K_i:



    def run(self):
        # подгрузка шрифта
        tc.console_set_custom_font(self.FONT_PATH, tc.FONT_TYPE_GREYSCALE | tc.FONT_LAYOUT_TCOD)
        # инициализация главной консоли
        with tc.console_init_root(self.scr_wd, self.scr_ht, title=self.GAME_NAME, fullscreen=False) as root_console:
            while True:
                # режим открытия карты
                if self.FOV_MODE:
                    self.__recompute_fov(self.player.x, self.player.y, self.fov_radius)
                # отрисовка сущностей
                rr.render_all(root_console, self.BARS_CONS, self.bars, self.player,
                              self.map, self.entities,
                              self.scr_wd, self.scr_ht, colors,
                              self.FOV_MODE, self.fov, self.msg_log)
                # вывод консоли
                tc.console_flush()
                # удаление предыдущих позиций
                rr.clear_all(root_console, self.entities)
                # получени ввода пользователя
                info = self.__keys_handler()
                # логгирование в консоль
                if info:
                    for item in info:
                        message = item.get('message')
                        maybe_dead_entity = item.get('dead')
                        new_item = item.get('new_item')

                        if message:
                            self.msg_log.add_message(message)

                        if maybe_dead_entity:
                            if isinstance(maybe_dead_entity, Player):
                                message, self.map.state = kill_player(maybe_dead_entity)
                                self.msg_log.add_message(message)
                            else:
                                message, state = kill_mob(maybe_dead_entity)
                                self.msg_log.add_message(message)

                        if new_item:
                            apply_info = self.player.apply_item(new_item)
                            info.extend(apply_info)
                            self.entities.remove(new_item)

                # обновление состояний
                if self.map.state == State.MOB_TURN:
                    # обновление поведения сущности, если она бот
                    for mob in self.entities[1:]:
                        info = mob.act(self.player, self.fov, self.map, self.entities)

                        if info:
                            for item in info:
                                message = item.get('message')
                                maybe_dead_entity = item.get('dead')
                                if message:
                                    self.msg_log.add_message(message)

                                if maybe_dead_entity:
                                    if isinstance(maybe_dead_entity, Player):
                                        message, self.map.state = kill_player(maybe_dead_entity)
                                        self.msg_log.add_message(message)
                                    else:
                                        message = kill_mob(maybe_dead_entity)
                                        self.msg_log.add_message(message)

                                    if self.map.state == State.PLAYER_DEAD:
                                        pass

                                if self.map.state == State.PLAYER_DEAD:
                                    pass

                    self.map.state = State.PLAYER_TURN


def starter(default_screen=False, dungeon=False, fov_mode=False, debug=False):
    if default_screen:
        return Engine(dungeon=dungeon, fov_mode=fov_mode, debug=debug)

    w = to_int(input("Please, input the screen width:  "))
    h = to_int(input("Please, input the screen height: "))
    return Engine(screen_width=w,
                  screen_height=h,
                  dungeon=dungeon,
                  fov_mode=fov_mode,
                  debug=debug)
