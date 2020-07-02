import tcod as tc

from logic.states import State
from logic.logger import OperationLog
from logic.patterns.command import Command
from logic.move import MoveType


class KeysHandler:
    @staticmethod
    def inventory_keys(engine, key):
        if key in [tc.event.K_ESCAPE, tc.event.K_i, tc.event.K_d]:
            if engine.prev_state.value:
                engine.curr_state.value = engine.prev_state.value
            else:
                engine.curr_state.value = State.PLAYER_TURN
            return OperationLog()

        if key == tc.event.K_1:
            return OperationLog([{'inv_index': 0}])
        if key == tc.event.K_2:
            return OperationLog([{'inv_index': 1}])
        if key == tc.event.K_3:
            return OperationLog([{'inv_index': 2}])

        return OperationLog()

    @staticmethod
    def user_input(engine):
        for event in tc.event.get():
            # debug
            if engine.info.DEBUG:
                if event.type != "MOUSEMOTION":
                    print(event)
            # quit
            if event.type == "QUIT":
                engine.IS_GAME = False
            # нажатие клавивиши
            if event.type == "KEYDOWN":
                # передача управления в инвентарь
                if engine.curr_state.value != State.PLAYER_DEAD and \
                        engine.curr_state.value in [State.SHOWING_MENU, State.DROP_ITEM]:
                    return Command(KeysHandler.inventory_keys, engine, event.sym)

                if event.sym == tc.event.K_ESCAPE:
                    # выход из инвентаря
                    if engine.curr_state.value == (State.SHOWING_MENU, State.DROP_ITEM):
                        engine.curr_state.value = engine.prev_state.value
                    else:
                        # выход из игры
                        engine.IS_GAME = False
                if engine.curr_state.value != State.PLAYER_DEAD:
                    if event.sym == tc.event.K_UP:
                        return KeysHandler.create_command(engine, MoveType.UP)
                    if event.sym == tc.event.K_DOWN:
                        return KeysHandler.create_command(engine, MoveType.DOWN)
                    if event.sym == tc.event.K_LEFT:
                        return KeysHandler.create_command(engine, MoveType.LEFT)
                    if event.sym == tc.event.K_RIGHT:
                        return KeysHandler.create_command(engine, MoveType.RIGHT)
                    if event.sym == tc.event.K_g:
                        return Command(engine.player.get_item, engine.entities)
                    if event.sym == tc.event.K_i:
                        # выход из меню инвентаря
                        if engine.curr_state.value == State.SHOWING_MENU:
                            engine.curr_state.value = engine.prev_state.value
                            return Command(lambda arg: arg, OperationLog())
                        # вход в меню инвентаря
                        return Command(lambda arg: arg, OperationLog([{'show_menu': True}]))
                    if event.sym == tc.event.K_d:
                        # выход из drop меню инвентаря
                        if engine.curr_state.value == State.DROP_ITEM:
                            engine.curr_state.value = engine.prev_state.value
                            return Command(lambda arg: arg, OperationLog())
                        # вход в drop меню инвентаря
                        return Command(lambda arg: arg, OperationLog([{'drop_menu': True}]))

        return Command(lambda arg: arg, OperationLog())

    @staticmethod
    def create_command(engine, move_type):
        return Command(engine.player.mv_handler.move, move_type,
                       engine.map, engine.entities, engine.curr_state)
