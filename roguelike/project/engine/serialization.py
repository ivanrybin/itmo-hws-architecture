"""
    Блок отвечающий за (де)сериализацию состояния игры в JSON.
    Используется для поддержки сохранений.
"""

import json
import os

from logic.entity_stats import EntityStats
from logic.inventory import Inventory, Armour, Item
from logic.logger import MessageLog
from logic.mob import Mob
from logic.player import *
from logic.patterns.strategy import *
from map.cell import *
from logic.states import State
from map.game_map import Map
from map.room import Room
from map.wall import Wall


def get_engine_stats(engine):
    engine_stats = {'engine': {
        'width': engine.scr_wd,
        'height': engine.scr_ht,
        'p_x': engine.player_init_x,
        'p_y': engine.player_init_y,
        'dungeon': engine.dungeon,
        'player_lvl': engine.player_lvl,
        'killed_on_lvl': engine.killed_on_lvl,
        'fov_mode': engine.FOV_MODE,
        'debug': engine.DEBUG,
        'FONT_PATH': engine.FONT_PATH,
        'GAME_NAME': engine.GAME_NAME
    }}
    if engine.prev_state:
        engine_stats['engine']['prev_state'] = engine.prev_state.value
    else:
        engine_stats['engine']['prev_state'] = None

    return engine_stats


def get_map_stats(engine):
    map_stats = {'map': {
        'state': engine.map.state.value,
        'walls': [],
        'rooms': [],
        'cells': []
    }
    }
    for wall in engine.map.walls:
        map_stats['map']['walls'].append({
            'x1': wall.x1,
            'x2': wall.x2,
            'y1': wall.y1,
            'y2': wall.y2,
        })

    for room in engine.map.rooms:
        map_stats['map']['rooms'].append({
            'x1': room.x1,
            'x2': room.x2,
            'y1': room.y1,
            'y2': room.y2,
        })

    for cells in engine.map.cells:
        lst = []
        for cell in cells:
            lst.append({
                'is_blocked': cell.is_blocked,
                'is_discovered': cell.is_discovered,
            })
        map_stats['map']['cells'].append(lst)

    return map_stats


def get_entities_stats(engine):
    entities_stats = {'entities': []}
    for entity in engine.entities[1:]:
        if entity.char == ord('#'):
            continue

        stat = {
            'x': entity.x,
            'y': entity.y,
            'ch': entity.char,
            'clr': entity.color,
            'name': entity.name,
            'strat': entity.strategy.__name__,
            'is_block': entity.is_blocking,
            'type': entity.type.value,
            'main_clr': entity.main_color,
            'stats': {
                'hp': entity.stats.hp,
                'max_hp': entity.stats.max_hp,
                'force': entity.stats.force,
                'defense': entity.stats.defense,
                'max_defense': entity.stats.max_defense
            }
        }
        if isinstance(entity.item, Armour):
            stat['item'] = {
                'defense': entity.item.defense,
                'max_defense': entity.item.max_defense,
                'color': entity.item.color
            }
        elif entity.item:
            stat['item'] = {}

        entities_stats['entities'].append(stat)
    return entities_stats


def get_player_stats(engine):
    player = engine.player
    player_stats = {'player': {
        'x': player.x,
        'y': player.y,
        'ch': player.char,
        'clr': player.color,
        'name': player.name,
        'is_block': player.is_blocking,
        'main_clr': player.main_color,
        'stats': {
            'hp': player.stats.hp,
            'max_hp': player.stats.max_hp,
            'force': player.stats.force,
            'defense': player.stats.defense,
            'max_defense': player.stats.max_defense,
        }
    }
    }

    if player.stats.armour:
        player_stats['player']['armour'] = {
            'x': player.stats.armour.x,
            'y': player.stats.armour.y,
            'ch': player.stats.armour.char,
            'clr': player.stats.armour.color,
            'name': player.stats.armour.name,
            'strat': player.stats.armour.strategy.__name__,
            'is_block': player.stats.armour.is_blocking,
            'type': player.stats.armour.type.value,
            'main_clr': player.stats.armour.main_color,
            'stats': {
                'hp': player.stats.armour.stats.hp,
                'max_hp': player.stats.armour.stats.max_hp,
                'force': player.stats.armour.stats.force,
                'defense': player.stats.armour.stats.defense,
                'max_defense': player.stats.armour.stats.max_defense,
            },
            'item': {
                'defense': player.stats.armour.item.defense,
                'max_defense': player.stats.armour.item.max_defense,
                'color': player.stats.armour.item.color
            }
        }
    player_stats['player']['inventory'] = {'size': len(player.inventory.items),
                                           'items': []}

    for item in player.inventory.items:
        player_stats['player']['inventory']['items'].append({
            'x': item.x,
            'y': item.y,
            'ch': item.char,
            'clr': item.color,
            'name': item.name,
            'strat': item.strategy.__name__,
            'is_block': item.is_blocking,
            'type': item.type.value,
            'main_clr': item.main_color,
            'stats': {
                'hp': item.stats.hp,
                'max_hp': item.stats.max_hp,
                'force': item.stats.force,
                'defense': item.stats.defense,
                'max_defense': item.stats.max_defense,
            },
            'item': {
                'defense': item.item.defense,
                'max_defense': item.item.max_defense,
                'color': item.item.color,
            }
        })

    return player_stats


def serialize_engine(engine):
    data = {
        **get_engine_stats(engine),
        **get_entities_stats(engine),
        **get_player_stats(engine),
        **get_map_stats(engine)
    }

    flag = 'x'
    if os.path.isfile('media/GAME_SAVE.json'):
        flag = 'w'

    with open('media/GAME_SAVE.json', flag, encoding='utf-8') as file:
        json.dump(data, file, indent=4)


def get_engine_from_stats(data, engine):
    engine.scr_wd = int(data['width'])
    engine.scr_ht = int(data['height'])
    engine.player_init_x = int(data['p_x'])
    engine.player_init_y = int(data['p_y'])
    engine.dungeon = data['dungeon']
    engine.player_lvl = int(data['player_lvl'])
    engine.killed_on_lvl = int(data['killed_on_lvl'])
    engine.fov_mode = bool(data['fov_mode'])
    engine.DEBUG = bool(data['debug'])
    engine.FONT_PATH = str(data['FONT_PATH'])
    engine.GAME_NAME = str(data['GAME_NAME'])
    if data['prev_state']:
        engine.prev_state = State(int(data['prev_state']))
    else:
        engine.prev_state = None
    engine.msg_log = MessageLog(0, 26, 3)
    engine.BARS_CONS = tc.console_new(engine.scr_wd, engine.scr_ht)
    engine.FOV_MODE = bool(data['fov_mode'])


def get_map_from_stats(data, engine):
    game_map = Map(engine.scr_wd,
                   engine.scr_ht,
                   engine.player_init_x,
                   engine.player_init_y)
    game_map.state = State.MOB_TURN

    game_map.cells = []
    for cells in data['cells']:
        row_cells = []
        for cell_stats in cells:
            cell = Cell(game_map.dungeon)
            cell.is_blocked = bool(cell_stats['is_blocked'])
            cell.is_discovered = bool(cell_stats['is_discovered'])
            row_cells.append(cell)

        game_map.cells.append(row_cells)

    game_map.rooms = []
    for room_stats in data['rooms']:
        room = Room(0, 0, 0, 0)
        room.x1, room.x2 = int(room_stats['x1']), int(room_stats['x2'])
        room.y1, room.y2 = int(room_stats['y1']), int(room_stats['y2'])

        game_map.rooms.append(room)

    game_map.walls = []
    for wall_stats in data['walls']:
        wall = Wall(0, 0, 0, 0)
        wall.x1, wall.x2 = int(wall_stats['x1']), int(wall_stats['x2'])
        wall.y1, wall.y2 = int(wall_stats['y1']), int(wall_stats['y2'])

        game_map.walls.append(wall)

    engine.map = game_map
    if engine.fov_mode:
        engine.fov_radius = 15
        engine.fov = engine._init_fov()


def get_player_from_stats(data, engine):
    # --------------------------------------------------
    def init_item(item_data):
        stats = EntityStats(hp=item_data['stats']['max_hp'],
                            force=item_data['stats']['force'],
                            defense=item_data['stats']['max_defense'])
        stats.hp = item_data['stats']['hp']
        stats.defense = item_data['stats']['defense']

        strat = PassiveStrategy
        if item_data['strat'] == 'PassiveStrategy':
            strat = PassiveStrategy
        elif item_data['strat'] == 'AggressiveStrategy':
            strat = AggressiveStrategy
        elif item_data['strat'] == 'CowardStrategy':
            strat = CowardStrategy

        item = Armour(defense=item_data['item']['max_defense'],
                      color=item_data['item']['color'])
        item.defense = item_data['item']['defense']

        mob = Mob(item_data['x'], item_data['y'],
                  screen_width=engine.scr_wd, screen_height=engine.scr_ht,
                  char=item_data['ch'], color=item_data['clr'],
                  name=item_data['name'], stats=stats,
                  game_map=engine.map, strategy=strat,
                  item=item,
                  is_blocking=bool(item_data['is_block']),
                  entity_type=EntityType(int(item_data['type']))
                  )

        mob.stats.owner = mob
        mob.mv_time = time.time()

        return mob

    # --------------------------------------------------
    stats = EntityStats(hp=10 * engine.player_lvl, force=2 * engine.player_lvl, defense=2 * engine.player_lvl)
    engine.player = Player(data['x'], data['y'],
                           screen_width=engine.scr_wd, screen_height=engine.scr_ht,
                           char=data['ch'], color=data['clr'], name=data['name'], stats=stats,
                           inventory=Inventory(3),
                           entity_type=EntityType.PLAYER)

    engine.player.stats.hp = data['stats']['hp']
    engine.player.stats.max_hp = data['stats']['max_hp']
    engine.player.stats.force = data['stats']['force']
    engine.player.stats.defense = data['stats']['defense']
    engine.player.stats.max_defense = data['stats']['max_defense']
    engine.player.stats.owner = engine.player
    engine.player.stats.armour = None

    if 'armour' in data:
        engine.player.stats.armour = init_item(data['armour'])

    inventory = Inventory(int(data['inventory']['size']))
    for item_stat in data['inventory']['items']:
        inventory.items.append(init_item(item_stat))

    engine.entities = [engine.player]


def get_entities_from_stats(data, engine):
    for entity in data:
        stats = EntityStats(hp=entity['stats']['max_hp'],
                            force=entity['stats']['force'],
                            defense=entity['stats']['max_defense'])
        stats.hp = entity['stats']['hp']
        stats.defense = entity['stats']['defense']

        strat = PassiveStrategy
        if entity['strat'] == 'PassiveStrategy':
            strat = PassiveStrategy
        elif entity['strat'] == 'AggressiveStrategy':
            strat = AggressiveStrategy
        elif entity['strat'] == 'CowardStrategy':
            strat = CowardStrategy

        e_type = EntityType(int(entity['type']))
        item = None
        if e_type == EntityType.ARMOUR:
            item = Armour(entity['item']['max_defense'], entity['item']['color'])
            item.defense = entity['item']['defense']
        elif 'item' in entity:
            item = Item()

        mob = Mob(entity['x'], entity['y'],
                  screen_width=engine.scr_wd, screen_height=engine.scr_ht,
                  char=entity['ch'], color=entity['clr'],
                  name=entity['name'], stats=stats,
                  game_map=engine.map, strategy=strat,
                  is_blocking=bool(entity['is_block']),
                  entity_type=EntityType(int(entity['type'])),
                  item=item
                  )

        mob.stats.owner = mob
        mob.mv_time = time.time()

        engine.entities.append(mob)


def deserialize_engine(engine):
    data = []
    with open('media/GAME_SAVE.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    get_engine_from_stats(data['engine'], engine)
    get_map_from_stats(data['map'], engine)
    get_player_from_stats(data['player'], engine)
    get_entities_from_stats(data['entities'], engine)

    return True
