import tcod as tc

import random as rnd

# logic
from logic.logger import MessageLog
from logic.patterns.decorator import MoveDeco
from logic.player import Player
from logic.mob import Mob
from logic.patterns.strategy import *
from logic.move import MoveType, MoveHandler
from logic.entity_stats import EntityStats
from logic.inventory import *

# map
from map.game_map import Map


class EngineInfo:
    def __init__(self, screen_width, screen_height, player_lvl, fov_mode, debug):
        self.scr_wd = int(screen_width)
        self.scr_ht = int(screen_height)
        self.player_lvl = player_lvl
        self.fov_radius = 15
        self.FOV_MODE = fov_mode
        self.DEBUG = debug

        self.killed_on_lvl = 0
        self.mobs_cnt = rnd.randint(10, 20)

        self.FONT_PATH = 'media/arial10x10.png'
        self.GAME_NAME = 'RogueLike SD - Ivan Rybin, Elizaveta Sidorova, ITMO JB SD SE'

        self.BARS_CONS = tc.console_new(self.scr_wd, self.scr_ht)
        self.msg_log = MessageLog(0, 26, 3)
        self.msg_log.add_message(Message(f"LEVEL: {self.player_lvl}", tc.yellow))
        self.msg_log.add_message(Message(f"YOU MUST KILL 3 AGGRS!", tc.light_red))

    def serialize(self):
        data = {
            "scr_wd": self.scr_wd,
            "scr_ht": self.scr_ht,
            "p_lvl": self.player_lvl,
            "kill_lvl": self.killed_on_lvl,
            "fov_mode": self.FOV_MODE,
            "DEBUG": self.DEBUG,
            "FONT_PATH": self.FONT_PATH,
            "GAME_NAME": self.GAME_NAME,
            "mobs_cnt": self.mobs_cnt
        }
        return data


class EngineInitializer:
    @staticmethod
    def init_map(engine):
        game_map = Map(engine.info.scr_wd,
                       engine.info.scr_ht,
                       int(engine.info.scr_wd * 0.03),
                       int(engine.info.scr_ht * 0.14))

        game_map.create_walls()
        return game_map

    @staticmethod
    def init_player(engine):
        lvl = engine.info.player_lvl
        stats = EntityStats(hp=10 * lvl, force=2 * lvl, defense=2 * lvl)
        player = Player(int(engine.info.scr_wd * 0.03),
                        int(engine.info.scr_ht * 0.14),
                        screen_width=engine.info.scr_wd,
                        screen_height=engine.info.scr_ht,
                        char=203, color=tc.white, name='Bob',
                        stats=stats,
                        inventory=Inventory(3),
                        entity_type=EntityType.PLAYER)

        player.mv_handler = MoveDeco(MoveHandler(player))
        player.stats.owner = player

        return player

    @staticmethod
    def create_mob(engine, left_prob, right_prob, mob_probs, mob_types, mob_stats):
        mob_type = mob_probs[(left_prob, right_prob)]
        mob_char, mob_colr, mob_name, mob_strat = mob_types[mob_type]
        mob_stat = mob_stats[mob_type]
        mob = Mob(None, None,
                  screen_width=engine.info.scr_wd,
                  screen_height=engine.info.scr_ht,
                  char=mob_char, color=mob_colr,
                  name=mob_name, stats=EntityStats(*mob_stat),
                  game_map=engine.map, strategy=mob_strat,
                  entity_type=EntityType.MOB)

        mob.stats.owner = mob
        return mob

    @staticmethod
    def create_item_entity(engine, left_prob, right_prob, items_probs, items_types, items_stats):
        item_type = items_probs[(left_prob, right_prob)]
        item_ch, item_clr, item_name, item_strat, item_real_t = items_types[item_type]
        item_stat = items_stats[item_type]
        item = Mob(None, None,
                   screen_width=engine.info.scr_wd, screen_height=engine.info.scr_ht,
                   char=item_ch, color=item_clr,
                   name=item_name, stats=EntityStats(*item_stat),
                   game_map=engine.map, strategy=item_strat,
                   item=Item(), is_blocking=False,
                   entity_type=item_real_t)

        if item_type == ItemType.ARMOUR_I:
            item.item = Armour(5, item.color)
        elif item_type == ItemType.ARMOUR_II:
            item.item = Armour(10, item.color)
        elif item_type == ItemType.HP_PTN:
            item.item = HealthPotion(5, item.color)
        elif item_type == ItemType.INTOX_PTN:
            item.item = IntoxPotion(7, item.color)
        item.stats.owner = item

        return item

    @staticmethod
    def init_entities(engine):
        lvl = engine.info.player_lvl
        # генерация мобов
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
        mob_stats = {'passive': (5 * lvl, 0, lvl),
                     'aggressive': (3 * lvl, 3 * lvl, 2 * lvl),
                     'coward': (1 * lvl, 0, 1 * lvl)}
        # случайный выбор типа моба
        for i in range(0, engine.info.mobs_cnt):
            prob = rnd.random()
            for left_prob, right_prob in mob_probs.keys():
                if left_prob < prob < right_prob:
                    mob = EngineInitializer.create_mob(engine, left_prob, right_prob,
                                                       mob_probs, mob_types, mob_stats)
                    mobs.append(mob)

        # создание Aggr'ов
        for i in range(0, 7):
            aggr = EngineInitializer.create_mob(engine, 1, 1, mob_probs, mob_types, mob_stats)
            aggr.stats.owner = aggr
            mobs.append(aggr)

        # генерация предметов
        items = []
        items_probs = {(0, 0.2): ItemType.HP_PTN,
                       (0.2, 0.4): ItemType.INTOX_PTN,
                       (0.4, 0.6): ItemType.ARMOUR_I,
                       (0.6, 0.8): ItemType.ARMOUR_II}

        items_types = {ItemType.HP_PTN:
                           (24, tc.light_sea, 'healing potion', PassiveStrategy, EntityType.HEALTH_PTN),
                       ItemType.INTOX_PTN:
                           (25, tc.light_violet, 'intoxicating potion', PassiveStrategy, EntityType.INTOX_PTN),
                       ItemType.ARMOUR_I:
                           (203, tc.light_blue, 'ARMOUR I', PassiveStrategy, EntityType.ARMOUR),
                       ItemType.ARMOUR_II:
                           (203, tc.light_yellow, 'ARMOUR II', PassiveStrategy, EntityType.ARMOUR)}

        items_stats = {ItemType.HP_PTN: (0, 0, 0),
                       ItemType.INTOX_PTN: (0, 0, 0),
                       ItemType.ARMOUR_I: (0, 0, 0),
                       ItemType.ARMOUR_II: (0, 0, 0)}

        for i in range(0, 10):
            prob = rnd.random()
            for left_prob, right_prob in items_probs.keys():
                if left_prob <= prob <= right_prob:
                    item_entity = EngineInitializer.create_item_entity(engine, left_prob, right_prob,
                                                                       items_probs, items_types, items_stats)
                    items.append(item_entity)

        return mobs + items

    @staticmethod
    def init_fov(engine):
        fov_map = tc.map_new(engine.map.wd, engine.map.ht)
        for x in range(engine.map.wd):
            for y in range(engine.map.ht):
                tc.map_set_properties(fov_map, x, y,
                                      not engine.map.cells[x][y].is_discovered,
                                      not engine.map.cells[x][y].is_blocked)
        return fov_map
