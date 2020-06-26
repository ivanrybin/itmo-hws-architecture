"""
    Блок отвечающий за (де)сериализацию состояния игры в JSON.
    Используется для поддержки сохранений.
"""

import json
import os

from engine.engine import Engine
from engine.engine_initializer import EngineInfo, EngineInitializer
from engine.render import RenderOrder, recompute_fov
from logic.entity_stats import EntityStats
from logic.inventory import Inventory, Armour, Item, ItemType, HealthPotion, IntoxPotion
from logic.mob import Mob
from logic.player import *
from logic.patterns.strategy import *
from map.cell import Cell
from map.game_map import Map
from map.wall import Wall


def save_game(engine):
    data = engine.serialize()

    flag = 'x'
    if os.path.isfile('media/GAME_SAVE.json'):
        flag = 'w'

    with open('media/GAME_SAVE.json', flag, encoding='utf-8') as file:
        json.dump(data, file, indent=4)


def deserialize_stats(data):
    stats = EntityStats(data['hp'], data['force'], data['defense'])
    stats.max_hp = data['max_hp']
    stats.max_defense = data['max_def']
    return stats


def deserialize_item(data):
    if not data:
        return Item()

    print(data)

    item_type = ItemType(int(data['type']))

    if item_type in [ItemType.ARMOUR_I, ItemType.ARMOUR_II]:
        item = Armour(defense=data['defense'], color=data['clr'], arm_type=item_type)
        item.max_defense = data['max_def']
        return item

    if item_type == ItemType.HP_PTN:
        item = HealthPotion(health_up=data['hp_up'], color=data['clr'])
        item.type = ItemType(int(data['type']))
        return item

    if item_type == ItemType.INTOX_PTN:
        item = IntoxPotion(intox_time=data['intox_time'], color=data['clr'])
        item.type = ItemType(int(data['type']))
        return item

    return Item()


def deserialize_inventory(data):
    inventory = Inventory(data['maxsize'])
    inventory.items = [deserialize_mob(item, None) for item in data['items']]
    return inventory


def deserialize_mob(data, move_handler):
    mob = Mob(data['x'], data['y'], data['scr_wd'], data['scr_ht'],
              data['ch'], data['clr'], data['name'],
              is_blocking=bool(data['is_block']),
              render_order=RenderOrder(int(data['render_ord'])),
              load_type='LOAD')

    mob.main_color = data['main_clr']
    mob.mv_handler = move_handler
    if mob.mv_handler:
        mob.mv_handler.owner = mob

    strat = PassiveStrategy
    if data['strat'] == 'PassiveStrategy':
        strat = PassiveStrategy
    elif data['strat'] == 'AggressiveStrategy':
        strat = AggressiveStrategy
    elif data['strat'] == 'CowardStrategy':
        strat = CowardStrategy

    mob.strategy = strat

    if data['stats']:
        mob.stats = deserialize_stats(data['stats'])
        mob.stats.owner = mob
    if data['item']:
        mob.item = deserialize_item(data['item'])
        mob.item.owner = mob
    if data['inventory']:
        mob.inventory = deserialize_inventory(data['inventory'])
        mob.inventory.owner = mob
    if data['type']:
        mob.type = EntityType(int(data['type']))

    return mob


def deserialize_info(data):
    info = EngineInfo(int(data['scr_wd']),
                      int(data['scr_ht']),
                      int(data['p_lvl']),
                      bool(data['fov_mode']),
                      bool(data['DEBUG']))

    info.killed_on_lvl = int(data["kill_lvl"])
    info.mobs_cnt = data["mobs_cnt"]
    info.FONT_PATH = data["FONT_PATH"]
    info.GAME_NAME = data["GAME_NAME"]

    return info


def deserialize_map(data):
    game_map = Map(data['width'], data['height'],
                   data['px'], data['py'],
                   load_type='LOAD')

    game_map.walls_cnt = data['walls_cnt']
    game_map.cells = [[Cell(bool(cell['is_blocked']),
                            bool(cell['is_discovered'])) for cell in cells]
                      for cells in data['cells']
                      ]
    game_map.walls = [Wall(wall['x'],
                           wall['y'],
                           wall['width'],
                           wall['height']) for wall in data['walls']
                      ]

    for wall in game_map.walls:
        game_map.create_wall(wall)

    return game_map


def deserialize_player(data, engine):
    player = EngineInitializer.init_player(engine)

    player.x = int(data['x'])
    player.y = int(data['y'])
    player.color = [int(x) for x in data['clr']]
    player.main_color = [int(x) for x in data['main_clr']]
    player.is_blocking = bool(data['is_block'])

    stats = deserialize_stats(data['stats'])
    if 'armour' in data and data['armour']:
        stats.armour = deserialize_mob(data['armour'], player.mv_handler)

    player.stats = stats
    player.stats.owner = player

    if data['inventory']['items']:
        inventory = deserialize_inventory(data['inventory'])
        player.inventory = inventory
        player.inventory.owner = player

    print(player.color)

    return player


def deserialize_entities(data):
    entities = []
    for entity_stats in data:
        entities.append(deserialize_mob(entity_stats, None))

    return entities


def deserialize_engine(data):
    info = deserialize_info(data['info'])
    engine = Engine(info.scr_wd, info.scr_ht)
    engine.info = info

    engine.map = deserialize_map(data['map'])
    engine.player = deserialize_player(data['player'], engine)
    engine.entities = [engine.player, *deserialize_entities(data['entities'])]

    if engine.info.FOV_MODE:
        engine.fov = EngineInitializer.init_fov(engine)
        recompute_fov(engine, engine.player.x, engine.player.y, engine.info.fov_radius)

    return engine


def load_game(file_path, is_save, scr_wd=80, scr_ht=40, fov_mode=False, debug=False):
    data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    engine = None
    if is_save:
        engine = deserialize_engine(data)
    else:
        engine = Engine(screen_width=scr_wd, screen_height=scr_ht, fov_mode=fov_mode, debug=debug)
        engine.map.walls = []
        engine.map.free_all_cells()
        for x, y in data['coords']:
            new_wall = Wall(x, y, 1, 1)
            engine.map.walls.append(new_wall)
            engine.map.cells[y][x].block()

        engine.player = EngineInitializer.init_player(engine)
        engine.entities = [engine.player, *EngineInitializer.init_entities(engine)]

    return engine
