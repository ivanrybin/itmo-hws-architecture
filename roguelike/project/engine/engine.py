"""
    Engine реализует движок игры.
    Через него происходят все операции, связанные с логикой и механикой игры.
"""

import json
import os

# render
from engine.render import Render, RenderOrder
# logic
from engine.engine_initializer import EngineInitializer, EngineInfo, EngineLoadTypes
from engine.keys_handler import KeysHandler
from logic.inventory import *
from logic.killer import kill_player, kill_mob
from logic.player import Player
from logic.states import State, StateHolder
from logic.patterns.strategy import AggressiveStrategy

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
        _, *mobs = self.entities
        data = {
            "info": self.info.serialize(),
            "player": self.player.serialize(),
            "entities": [m.serialize() for m in mobs],
            "map": self.map.serialize()
        }
        return data

    @staticmethod
    def stop_engine(engine):
        engine.IS_GAME = False
        engine.curr_state = State.PLAYER_DEAD
        return OperationLog([{'message': Message('ENGINE WAS STOPPED.', tc.yellow)}])

    def get_command(self):
        command = None
        if self.load_type == EngineLoadTypes.TEST:
            command = self.tester.get_command(self)
        elif self.load_type in [EngineLoadTypes.LOAD, EngineLoadTypes.NORMAL]:
            command = KeysHandler.user_input(self)
        return command

    def player_turn(self):
        command = self.get_command()
        operation_log = command.execute()

        # логгирование в консоль
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
                message = maybe_dead_entity.die()
                if isinstance(maybe_dead_entity, Player):
                    self.curr_state.value = State.PLAYER_DEAD
                else:
                    if isinstance(maybe_dead_entity.strategy, AggressiveStrategy):
                        self.info.killed_on_lvl += 1
                self.info.msg_log.add_message(message)

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
                item = self.player.inventory.items[is_index]
                if self.curr_state.value == State.SHOWING_MENU:
                    operation_log.log.extend(self.player.inventory.activate_item(item).log)
                elif self.curr_state.value == State.DROP_ITEM:
                    operation_log.log.extend(
                        self.player.inventory.drop_item(self.entities, item).log)

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
        if self.curr_state.value != State.MOB_TURN:
            return

        # обновление поведения сущности, если она бот
        _, *mobs = self.entities
        for mob in mobs:
            operation_log = mob.act(self.player, self.fov, self.map, self.entities)

            if not operation_log or not operation_log.log:
                continue

            for item in operation_log.log:
                message = item.get('message')
                if message:
                    self.info.msg_log.add_message(message)

                maybe_dead_entity = item.get('dead')
                if maybe_dead_entity:
                    message = maybe_dead_entity.die()
                    if isinstance(maybe_dead_entity, Player):
                        self.curr_state.value = State.PLAYER_DEAD
                    self.info.msg_log.add_message(message)

        if self.curr_state.value != State.PLAYER_DEAD:
            self.curr_state.value = State.PLAYER_TURN

    def stop(self):
        self.IS_GAME = False

    def game_exit(self):
        # если игрок не мертв и мы вышли - сохраняем игру
        if self.curr_state.value != State.PLAYER_DEAD and self.load_type != EngineLoadTypes.TEST:
            save_game(self)
        elif self.load_type != EngineLoadTypes.TEST:
            # удаляем сохранение при смерти
            if os.path.isfile('media/GAME_SAVE.json'):
                os.remove('media/GAME_SAVE.json')

    def init_console_font(self):
        # подгрузка шрифта
        tc.console_set_custom_font(self.info.FONT_PATH, tc.FONT_TYPE_GREYSCALE | tc.FONT_LAYOUT_TCOD)

    def run(self):
        self.init_console_font()
        # инициализация главной консоли
        with tc.console_init_root(self.info.scr_wd,
                                  self.info.scr_ht,
                                  title=self.info.GAME_NAME, fullscreen=False) as root_console:
            while self.IS_GAME:
                # режим открытия карты
                if self.info.FOV_MODE:
                    Render.recompute_fov(self, self.player.x, self.player.y, self.info.fov_radius)
                # отрисовка сущностей
                Render.render_all(root_console, self.info.BARS_CONS, self.player,
                                  self.map, self.entities,
                                  self.info.scr_wd, self.info.scr_ht, colors,
                                  self.info.FOV_MODE, self.fov, self.info.msg_log, self.curr_state)
                # вывод консоли
                tc.console_flush()
                # удаление предыдущих позиций
                Render.clear_all(root_console, self.entities)
                # ход игрока
                self.player_turn()
                # ход мобов
                self.mob_turn()

        self.game_exit()
