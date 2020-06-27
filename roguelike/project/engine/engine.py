"""
    Engine реализует движок игры.
    Через него происходят все операции, связанные с логикой и механикой игры.
"""

import tcod as tc
import random as rnd
import json
import os

# render
import engine.render as rr

# logic
from engine.engine_initializer import EngineInitializer, EngineInfo, EngineLoadTypes
from engine.keys_handler import KeysHandler
from logic.patterns.command import Command
from logic.player import Player
from logic.states import State, StateHolder
from logic.killer import kill_player, kill_mob
from logic.inventory import *
from test import EngineTester

colors = {'fov_dark_walls': tc.Color(0, 5, 90),
          'fov_dark_background': tc.Color(45, 45, 140),
          'main_wall': tc.Color(167, 103, 65),
          'main_ground': tc.Color(0, 30, 30),
          'kate_ground': tc.Color(200, 146, 7)}


def save_game(engine):
    data = engine.serialize()

    flag = 'x'
    if os.path.isfile('media/GAME_SAVE.json'):
        flag = 'w'

    with open('media/GAME_SAVE.json', flag, encoding='utf-8') as file:
        json.dump(data, file, indent=4)


class Engine:
    def __init__(self, screen_width=80, screen_height=40, fov_mode=False, debug=False, player_lvl=1,
                 load_type=EngineLoadTypes.NORMAL, tester=None):
        # состояние игры
        self.IS_GAME = True
        self.load_type = load_type
        self.curr_state = StateHolder(State.PLAYER_TURN)
        self.prev_state = StateHolder(State.PLAYER_TURN)
        if load_type == EngineLoadTypes.LOAD:
            return
        # держатель всех характеристик
        self.info = EngineInfo(screen_width, screen_height, player_lvl, fov_mode, debug)
        # инициализация среды
        self.map = EngineInitializer.init_map(self, load_type)
        self.player = EngineInitializer.init_player(self, load_type)
        self.entities = [self.player, *EngineInitializer.init_entities(self, load_type)]
        self.fov = None
        if fov_mode:
            self.fov = EngineInitializer.init_fov(self)
        if load_type == EngineLoadTypes.TEST:
            self.tester = tester

    def serialize(self):
        data = {
            "info": self.info.serialize(),
            "player": self.player.serialize(),
            "entities": [e.serialize() for e in self.entities[1:]],
            "map": self.map.serialize()
        }
        return data

    @staticmethod
    def stop_engine(engine):
        engine.IS_GAME = False
        engine.curr_state = State.PLAYER_DEAD
        return OperationLog([{'message': Message('ENGINE WAS STOPPED.', tc.yellow)}])

    def player_turn(self):
        command = None
        if self.load_type == EngineLoadTypes.TEST:
            command = self.tester.get_command(self)
        elif self.load_type in [EngineLoadTypes.LOAD, EngineLoadTypes.NORMAL]:
            command = KeysHandler.user_input(self)
        # паттерн команда
        operation_log = command.execute()
        # логгирование в консоль
        if operation_log.log:
            for item in operation_log.log:
                message = item.get('message')
                maybe_dead_entity = item.get('dead')
                picked_item = item.get('new_item')
                is_menu_key = item.get('show_menu')
                is_drop_meny_key = item.get('drop_menu')
                is_index = item.get('inv_index')
                is_drop = item.get('drop_item')

                if message:
                    self.info.msg_log.add_message(message)

                if maybe_dead_entity:
                    if isinstance(maybe_dead_entity, Player):
                        message, self.curr_state.value = kill_player(maybe_dead_entity)
                        self.curr_state.value = State.PLAYER_DEAD
                        self.info.msg_log.add_message(message)
                    else:
                        is_aggr, message, state = kill_mob(maybe_dead_entity)
                        self.info.msg_log.add_message(message)
                        if is_aggr:
                            self.info.killed_on_lvl += 1

                if picked_item:
                    operation_log.log.extend(self.player.pick_item(picked_item).log)
                    self.entities.remove(picked_item)

                if is_menu_key:
                    self.prev_state.value = self.curr_state.value
                    self.curr_state.value = State.SHOWING_MENU

                if is_drop_meny_key:
                    self.prev_state.value = self.curr_state.value
                    self.curr_state.value = State.DROP_ITEM

                if is_index is not None and is_index >= 0 and \
                        self.prev_state.value != State.PLAYER_DEAD:
                    if is_index >= len(self.player.inventory.items):
                        operation_log.add_item({'message': Message('Wrong item index.', tc.yellow)})
                        continue

                    item = self.player.inventory.items[is_index]

                    if self.curr_state.value == State.SHOWING_MENU:
                        operation_log.log.extend(self.player.inventory.activate_item(item).log)
                    elif self.curr_state.value == State.DROP_ITEM:
                        operation_log.log.extend(self.player.inventory.drop_item(self.entities, item).log)

                if is_drop:
                    self.prev_state.value = self.curr_state.value
                    self.curr_state.value = State.DROP_ITEM

                if self.info.killed_on_lvl >= 3:
                    self.__init__(self.info.scr_wd,
                                  self.info.scr_ht,
                                  fov_mode=self.info.FOV_MODE,
                                  debug=self.info.DEBUG,
                                  player_lvl=self.info.player_lvl + 1)
                    continue

    def mob_turn(self):
        if self.curr_state.value == State.MOB_TURN:
            # обновление поведения сущности, если она бот
            for mob in self.entities[1:]:
                operation_log = mob.act(self.player, self.fov, self.map, self.entities)

                if operation_log and operation_log.log:
                    for item in operation_log.log:
                        message = item.get('message')
                        maybe_dead_entity = item.get('dead')
                        if message:
                            self.info.msg_log.add_message(message)

                        if maybe_dead_entity:
                            if isinstance(maybe_dead_entity, Player):
                                message, self.curr_state.value = kill_player(maybe_dead_entity)
                                self.info.msg_log.add_message(message)
                                self.curr_state.value = State.PLAYER_DEAD
                            else:
                                message = kill_mob(maybe_dead_entity)
                                self.info.msg_log.add_message(message)

            if self.curr_state.value != State.PLAYER_DEAD:
                self.curr_state.value = State.PLAYER_TURN

    def stop(self):
        self.IS_GAME = False

    def run(self):
        # подгрузка шрифта
        tc.console_set_custom_font(self.info.FONT_PATH, tc.FONT_TYPE_GREYSCALE | tc.FONT_LAYOUT_TCOD)
        # инициализация главной консоли
        with tc.console_init_root(self.info.scr_wd,
                                  self.info.scr_ht,
                                  title=self.info.GAME_NAME, fullscreen=False) as root_console:
            while self.IS_GAME:
                # режим открытия карты
                if self.info.FOV_MODE:
                    rr.recompute_fov(self, self.player.x, self.player.y, self.info.fov_radius)
                # отрисовка сущностей
                rr.render_all(root_console, self.info.BARS_CONS, self.player,
                              self.map, self.entities,
                              self.info.scr_wd, self.info.scr_ht, colors,
                              self.info.FOV_MODE, self.fov, self.info.msg_log, self.curr_state)
                # вывод консоли
                tc.console_flush()
                # удаление предыдущих позиций
                rr.clear_all(root_console, self.entities)
                # ход игрока
                self.player_turn()
                # ход мобов
                self.mob_turn()

        # если игрок не мертв и мы вышли - сохраняем игру
        if self.curr_state.value != State.PLAYER_DEAD and self.load_type != EngineLoadTypes.TEST:
            save_game(self)
        elif self.load_type != EngineLoadTypes.TEST:
            # удаляем сохранение при смерти
            if os.path.isfile('media/GAME_SAVE.json'):
                os.remove('media/GAME_SAVE.json')
