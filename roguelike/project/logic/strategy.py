import time
import random as rnd

class Strategy:
    @staticmethod
    def act(mob, game_map):
        """
        Стандартное поведение, случайное движение по карте.
        В конфликт не вступает.
        """
        if 'mv_wait' not in mob.__dict__:
            mob.mv_wait = rnd.randint(1, 3)
        if 'mv_time' not in mob.__dict__:
            mob.mv_time = time.time()

        if time.time() - mob.mv_time < mob.mv_wait:
            return

        mob.mv_time = time.time()

        dx = rnd.randint(-1, 1)
        dy = 0
        if dx == 0:
            dy = rnd.randint(-1, 1)

        if game_map.is_cell_blocked(mob.x + dx, mob.y + dy):
            return

        if 0 <= mob.x + dx < mob.sw:
            mob.x += dx
        elif mob.x + dx >= mob.sw:
            mob.x = mob.sw - 1
        elif mob.x + dx < 0:
            mob.x = 0

        if 0 <= mob.y + dy < mob.sh:
            mob.y += dy
        elif mob.y + dy >= mob.sh:
            mob.y = mob.sh - 1
        elif mob.y + dy < 0:
            mob.y = 0


class PassiveStrategy(Strategy):
    pass


class AgressiveStrategy(Strategy):
    @staticmethod
    def act(mob, game_map):
        print("hi")


class CowardStrategy(Strategy):
    @staticmethod
    def act(mob, game_map):
        print("hi")
