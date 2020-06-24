import tcod as tc
import random as rnd
import os

# render
import engine.render as rr
from engine.bar import Bar

# logic
from engine.serialization import serialize_engine, deserialize_engine
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
    def __init__(self, screen_width=80, screen_height=40, dungeon=False, fov_mode=False, debug=False, player_lvl=1,
                 load_type='NORMAL'):
        if load_type == 'LOAD':
            return

        self.scr_wd = to_int(screen_width)
        self.scr_ht = to_int(screen_height)
        self.player_init_x = to_int(screen_width * 0.03)
        self.player_init_y = to_int(screen_height * 0.15)
        # инициализация среды
        self.player_lvl = player_lvl
        self.dungeon = dungeon
        self.map = self.__init_map()
        self.player = self.__init_player()
        self.entities = [self.player, *self.__init_mobs()]
        self.fov = None
        if fov_mode:
            self.fov = self._init_fov()
            self.fov_radius = 15
        self.whoes_state = State.PLAYER_TURN
        self.killed_on_lvl = 0
        self.prev_state = None
        # служебные штуки
        self.msg_log = MessageLog(0, 26, 3)
        self.BARS_CONS = tc.console_new(self.scr_wd, self.scr_ht)
        self.FOV_MODE = fov_mode
        self.DEBUG = debug
        self.FONT_PATH = 'media/arial10x10.png'
        self.GAME_NAME = 'RogueLike SD - Ivan Rybin, Elizaveta Sidorova, ITMO JB SD SE'
        self.msg_log.add_message(Message(f"LEVEL: {self.player_lvl}", tc.yellow))
        self.msg_log.add_message(Message(f"YOU MUST KILL 3 AGGRS!", tc.light_red))

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
        stats = EntityStats(hp=10 * self.player_lvl, force=2 * self.player_lvl, defense=2 * self.player_lvl)
        player = Player(self.player_init_x, self.player_init_y,
                        screen_width=self.scr_wd, screen_height=self.scr_ht,
                        char=203, color=tc.white, name='Bob', stats=stats,
                        inventory=Inventory(3),
                        entity_type=EntityType.PLAYER)
        player.stats.owner = player

        return player

    def __init_mobs(self, cnt=rnd.randint(10, 20)):
        mob_chars = [197, 185, 180, 206, 205, 178]
        mob_colors = [tc.darker_green, tc.dark_flame, tc.dark_azure, tc.gold, tc.gray,
                      tc.green, tc.black, tc.blue, tc.dark_orange, tc.dark_cyan]

        mobs = []
        # вероятности появления пугливых, пассивных, агрессивных
        mob_probs = {(0, 0.2): 'coward',
                     (0.2, 0.6): 'passive',
                     (1, 1): 'aggressive'}
        # символ, цвет, стратегия моба
        mob_types = {'passive': (205, tc.dark_green, 'Cow', PassiveStrategy),
                     'aggressive': (206, tc.dark_flame, 'Aggr', AggressiveStrategy),
                     'coward': (197, tc.light_cyan, 'Aaaa', CowardStrategy)}
        # характеристика мобов: здоровье, сила, защита
        mob_stats = {'passive': (5 * self.player_lvl, 0, 1 * 1 * self.player_lvl),
                     'aggressive': (3 * self.player_lvl, 3 * self.player_lvl, 2 * 1 * self.player_lvl),
                     'coward': (1 * self.player_lvl, 0, 1 * self.player_lvl)}
        # случайный выбор типа моба
        for i in range(0, cnt):
            prob = rnd.random()
            for left_prob, right_prob in mob_probs.keys():
                if left_prob < prob < right_prob:
                    mob_type = mob_probs[(left_prob, right_prob)]
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

        for i in range(0, 7):
            mob_type = mob_probs[(1, 1)]
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
        items = []
        items_probs = {(0, 0.2): 'healing',
                       (0.2, 0.4): 'intoxicating',
                       (0.4, 0.6): 'armour I',
                       (0.6, 0.8): 'armour II'}

        items_types = {'healing': (24, tc.light_sea, 'healing potion', PassiveStrategy, EntityType.HEALTH_PTN),
                       'intoxicating': (25, tc.light_violet, 'intoxicating potion', PassiveStrategy, EntityType.INTOX_PTN),
                       'armour I': (203, tc.light_blue, 'ARMOUR I', PassiveStrategy, EntityType.ARMOUR),
                       'armour II': (203, tc.light_yellow, 'ARMOUR II', PassiveStrategy, EntityType.ARMOUR)}

        items_stats = {'healing': (0, 0, 0),
                       'intoxicating': (0, 0, 0),
                       'armour I': (0, 0, 0),
                       'armour II': (0, 0, 0)}

        for i in range(0, 10):
            prob = rnd.random()
            for left_prob, right_prob in items_probs.keys():
                if left_prob <= prob <= right_prob:
                    item_type = items_probs[(left_prob, right_prob)]
                    item_ch, item_clr, item_name, item_strat, item_real_t = items_types[item_type]
                    item_stat = items_stats[item_type]
                    item = Mob(None, None,
                               screen_width=self.scr_wd, screen_height=self.scr_ht,
                               char=item_ch, color=item_clr,
                               name=item_name, stats=EntityStats(*item_stat),
                               game_map=self.map, strategy=item_strat,
                               item=Item(), is_blocking=False,
                               entity_type=item_real_t)

                    if item_type == 'armour I':
                        item.item = Armour(5, item.color)
                    elif item_type == 'armour II':
                        item.item = Armour(10, item.color)
                    item.stats.owner = item
                    items.append(item)

        return mobs + items

    def _init_fov(self):
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

    def __inventory_keys_handler(self, key):
        if key in [tc.event.K_ESCAPE, tc.event.K_i, tc.event.K_d]:
            if self.prev_state:
                self.map.state = self.prev_state
            else:
                self.map.state = State.PLAYER_TURN
            return []

        if key == tc.event.K_1:
            return [{'inv_index': 0}]
        if key == tc.event.K_2:
            return [{'inv_index': 1}]
        if key == tc.event.K_3:
            return [{'inv_index': 2}]

        return []

    def __keys_handler(self):
        for event in tc.event.get():
            # debug
            if self.DEBUG:
                if event.type != "MOUSEMOTION":
                    print(event)
            # quit
            if event.type == "QUIT":
                self.IS_GAME = False
            # нажатие клавивиши
            if event.type == "KEYDOWN":
                # передача управления в инвентарь
                if self.map.state != State.PLAYER_DEAD and self.map.state in [State.SHOWING_MENU, State.DROP_ITEM]:
                    return self.__inventory_keys_handler(event.sym)

                if event.sym == tc.event.K_ESCAPE:
                    # выход из инвентаря
                    if self.map.state == (State.SHOWING_MENU, State.DROP_ITEM):
                        self.map.state = self.prev_state
                    else:
                        # выход из игры
                        self.IS_GAME = False
                if self.map.state != State.PLAYER_DEAD:
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
                    if event.sym == tc.event.K_i:
                        # выход из меню инвентаря
                        if self.map.state == State.SHOWING_MENU:
                            self.map.state = self.prev_state
                            print(self.map.state)
                            return []
                        # вход в меню инвентаря
                        return [{'show_menu': True}]
                    if event.sym == tc.event.K_d:
                        # выход из drop меню инвентаря
                        if self.map.state == State.DROP_ITEM:
                            self.map.state = self.prev_state
                            return []
                        # вход в drop меню инвентаря
                        return [{'drop_menu': True}]

    def run(self):
        self.IS_GAME = True
        # подгрузка шрифта
        tc.console_set_custom_font(self.FONT_PATH, tc.FONT_TYPE_GREYSCALE | tc.FONT_LAYOUT_TCOD)
        # инициализация главной консоли
        with tc.console_init_root(self.scr_wd, self.scr_ht, title=self.GAME_NAME, fullscreen=False) as root_console:
            while self.IS_GAME:
                # режим открытия карты
                if self.FOV_MODE:
                    self.__recompute_fov(self.player.x, self.player.y, self.fov_radius)
                # отрисовка сущностей
                rr.render_all(root_console, self.BARS_CONS, self.player,
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
                        picked_item = item.get('new_item')
                        is_menu_key = item.get('show_menu')
                        is_drop_meny_key = item.get('drop_menu')
                        is_index = item.get('inv_index')
                        is_drop = item.get('drop_item')

                        if message:
                            self.msg_log.add_message(message)

                        if maybe_dead_entity:
                            if isinstance(maybe_dead_entity, Player):
                                message, self.map.state = kill_player(maybe_dead_entity)
                                self.map.state = State.PLAYER_DEAD
                                self.msg_log.add_message(message)
                            else:
                                is_aggr, message, state = kill_mob(maybe_dead_entity)
                                self.msg_log.add_message(message)
                                if is_aggr:
                                    self.killed_on_lvl += 1

                        if picked_item:
                            apply_info = self.player.pick_item(picked_item)
                            info.extend(apply_info)
                            self.entities.remove(picked_item)

                        if is_menu_key:
                            self.prev_state = self.map.state
                            self.map.state = State.SHOWING_MENU

                        if is_drop_meny_key:
                            self.prev_state = self.map.state
                            self.map.state = State.DROP_ITEM

                        if is_index is not None and is_index >= 0 and self.prev_state != State.PLAYER_DEAD:
                            if is_index >= len(self.player.inventory.items):
                                info.append({'message': Message('Wrong item index.', tc.yellow)})
                                continue

                            item = self.player.inventory.items[is_index]

                            if self.map.state == State.SHOWING_MENU:
                                info.extend(self.player.inventory.activate_item(item))
                            elif self.map.state == State.DROP_ITEM:
                                info.extend(self.player.inventory.drop_item(self.entities, item))

                        if is_drop:
                            self.prev_state = self.map.state
                            self.map.state = State.DROP_ITEM

# ---------------------- GAME LVL UP
                        if self.killed_on_lvl >= 3:
                            self.__init__(self.scr_wd, self.scr_ht, self.dungeon,
                                          fov_mode=self.FOV_MODE, debug=self.DEBUG,
                                          player_lvl=self.player_lvl + 1)
                            continue
# ---------------------- GAME LVL UP

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
                                        self.map.state = State.PLAYER_DEAD
                                    else:
                                        message = kill_mob(maybe_dead_entity)
                                        self.msg_log.add_message(message)

                                    if self.map.state == State.PLAYER_DEAD:
                                        pass

                                if self.map.state == State.PLAYER_DEAD:
                                    pass

                    if self.map.state != State.PLAYER_DEAD:
                        self.map.state = State.PLAYER_TURN

        if self.map.state != State.PLAYER_DEAD:
            serialize_engine(self)
        else:
            if os.path.isfile('media/GAME_SAVE.json'):
                os.remove('media/GAME_SAVE.json')


def starter(default_screen=False, dungeon=False, fov_mode=False, debug=False):
    if os.path.isfile('media/GAME_SAVE.json'):
        new_or_save = str(input('Load save game - print 1, else - 0: '))
        if new_or_save == '1':
            engine = Engine(load_type='LOAD')
            deserialize_engine(engine)
            return engine

    if default_screen:
        return Engine(dungeon=dungeon, fov_mode=fov_mode, debug=debug)

    w = to_int(input("Please, input the screen width:  "))
    h = to_int(input("Please, input the screen height: "))
    return Engine(screen_width=w,
                  screen_height=h,
                  dungeon=dungeon,
                  fov_mode=fov_mode,
                  debug=debug)
