from time import time

from engine.engine import *
from logic.entity_stats import EntityStats
from logic.mob import Mob
from logic.move import MoveType
from logic.patterns.strategy import PassiveStrategy
from logic.patterns.command import Command


class EngineTester:
    def __init__(self):
        self.moves = [MoveType.DOWN, MoveType.DOWN, MoveType.DOWN,
                      MoveType.RIGHT, MoveType.UP, MoveType.LEFT]
        self.tests = [
            # move test
            *EngineTester.__move_test_moves(self.moves),
            EngineTester.player_move_test,
            # pick test
            lambda _, engine: EngineTester.__item_for_pick(_, engine, item_type=EntityType.ARMOUR),
            lambda _, engine: EngineTester.__move_player(engine, MoveType.RIGHT),
            EngineTester.__pick_item,
            EngineTester.item_pick_test,
            EngineTester.__open_pick_inventory,
            EngineTester.opened_menu_test,
            # activate test
            EngineTester.__activate_item,
            EngineTester.item_activate_test,
            EngineTester.__close_inventory,
            EngineTester.closed_menu_test,
            # drunk test
            lambda _, engine: EngineTester.__item_for_pick(_, engine, item_type=EntityType.INTOX_PTN),
            lambda _, engine: EngineTester.__move_player(engine, MoveType.RIGHT),
            EngineTester.__pick_item,
            EngineTester.__activate_item,
            EngineTester.__fix_player_pos,
            lambda _, engine: EngineTester.__move_player(engine, MoveType.RIGHT),
            EngineTester.intox_test,
            # stop all tests and engine
            EngineTester.stop_tests
        ]
        self.last_time = time()

    def get_command(self, engine):
        while time() - self.last_time < 1:
            pass
        test = self.tests.pop(0)
        self.last_time = time()
        return test(self, engine)

    @staticmethod
    def stop_tests(_, engine):
        return Command(Engine.stop_engine, engine)

    @staticmethod
    def __fix_player_pos(self, engine):
        self.player_x = engine.player.x
        self.player_y = engine.player.y
        return Command(lambda arg: arg, OperationLog())

    @staticmethod
    def __move_player(engine, mv_type=None):
        return Command(engine.player.mv_handler.move, mv_type, engine.map, engine.get_entities(), engine.curr_state)

    @staticmethod
    def __move_test_moves(mv_types):
        moves = []
        for move_type in mv_types:
            moves.append(lambda self, eng, mv_type=move_type:
                         EngineTester.__move_player(eng, mv_type=mv_type))
        return moves

    def player_move_test(self, engine):
        dx, dy = 0, 0
        for move in self.moves:
            if move == MoveType.DOWN:
                dy += 1
            if move == MoveType.UP:
                dy -= 1
            if move == MoveType.LEFT:
                dx -= 1
            if move == MoveType.RIGHT:
                dx += 1

        assert engine.player.x == engine.map.px + dx
        assert engine.player.y == engine.map.py + dy
        print('MOVE TEST - OK')
        return Command(lambda arg: arg, OperationLog([{'message': Message('MOVE TEST - OK', tc.white)}]))

    @staticmethod
    def __item_for_pick(_, engine, item_type=EntityType.ARMOUR):
        item = Mob(Item(tc.light_blue, item_type), engine.player.x + 1, engine.player.y, load_type='TEST',
                   screen_width=engine.info.scr_wd, screen_height=engine.info.scr_ht,
                   char=203, color=tc.light_blue, name="test item",
                   stats=EntityStats(*(0, 0, 0)), game_map=engine.map,
                   strategy=PassiveStrategy(),
                   is_blocking=False, entity_type=item_type)
        if item_type == EntityType.ARMOUR:
            item.item = Armour(5, item.color)
            item.char = 203
            item.color = tc.light_blue
        elif item_type == EntityType.INTOX_PTN:
            item.item = IntoxPotion(7, item.color)
            item.char = 25
            item.color = tc.light_violet
        item.stats.owner = item

        engine.mobs.append(item)

        return Command(lambda arg: arg,
                       OperationLog([{'message': Message('Created item for pick.', tc.yellow)}]))

    @staticmethod
    def __pick_item(_, engine):
        return Command(engine.player.get_item, engine.get_entities())

    @staticmethod
    def __open_drop_inventory(_, engine):
        return Command(lambda arg: arg, OperationLog([{'drop_menu': True}]))

    @staticmethod
    def __open_pick_inventory(_, engine):
        return Command(lambda arg: arg, OperationLog([{'show_menu': True}]))

    @staticmethod
    def __close_inventory(_, engine):
        engine.curr_state.value = State.PLAYER_TURN
        return Command(lambda arg: arg, OperationLog())

    @staticmethod
    def __activate_item(_, engine):
        return Command(lambda arg: arg, OperationLog([{'inv_index': 0}]))

    @staticmethod
    def item_pick_test(_, engine):
        assert len(engine.player.inventory.items) == 1
        print('PICK TEST - OK')
        return Command(lambda arg: arg, OperationLog([{'message': Message('PICK TEST - OK', tc.white)}]))

    @staticmethod
    def item_activate_test(_, engine):
        assert len(engine.player.inventory.items) == 0
        assert engine.player.color == engine.player.stats.armour.color
        print('ACTIVATE TEST - OK')
        return Command(lambda arg: arg, OperationLog([{'message': Message('ACTIVATE TEST - OK', tc.white)}]))

    @staticmethod
    def opened_menu_test(_, engine):
        assert engine.curr_state.value == State.SHOWING_MENU
        print('OPENED MENU TEST - OK')
        return Command(lambda arg: arg, OperationLog([{'message': Message('OPENED MENU TEST - OK', tc.white)}]))

    @staticmethod
    def closed_menu_test(_, engine):
        assert engine.curr_state.value == State.PLAYER_TURN
        print('CLOSED MENU TEST - OK')
        return Command(lambda arg: arg, OperationLog([{'message': Message('CLOSED MENU TEST - OK', tc.white)}]))

    @staticmethod
    def intox_test(self, engine):
        assert engine.player.y != self.player_y
        print('INTOX POTION TEST - OK')
        return Command(lambda arg: arg, OperationLog([{'message': Message('INTOX POTION TEST - OK', tc.white)}]))


class TestRunner:
    @staticmethod
    def start_tests():
        engine = Engine(load_type=EngineLoadTypes.TEST, tester=EngineTester())
        engine.run()


if __name__ == '__main__':
    TestRunner.start_tests()
