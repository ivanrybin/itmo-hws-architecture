"""
    Map реализует игровую карту.
"""

import random as rnd

from map.cell import Cell
from map.room import Wall


class Map:
    def __init__(self, width, height, player_start_x, player_start_y, load_type='NORMAL'):
        self.wd = width
        self.ht = height
        self.px = player_start_x
        self.py = player_start_y
        self.walls = []
        self.rooms = [Wall(self.px - 5, self.py - 5, 10, 10)]
        if load_type == 'LOAD':
            return
        self.walls_cnt = rnd.randint(5, 10)
        self.cells = self.__init_cells()

    def serialize(self):
        data = {
            'width': self.wd,
            'height': self.ht,
            'px': self.px,
            'py': self.py,
            'walls_cnt': self.walls_cnt,
            'cells': [[cell.serialize() for cell in cells] for cells in self.cells],
            'walls': [wall.serialize() for wall in self.walls],
            'rooms': [room.serialize() for room in self.rooms]
        }

        return data

    def __init_cells(self):
        cells = [[Cell(False) for y in range(self.ht)] for x in range(self.wd)]
        return cells

    def create_wall(self, wall):
        for x in range(max(0, min(wall.x_left, self.wd)), max(0, min(wall.x_right, self.wd))):
            for y in range(max(0, min(wall.y_bottom, self.ht)), max(0, min(wall.y_top, self.ht))):
                self.cells[x][y].block()

    def create_walls(self, with_intersection=False):
        cnt = self.walls_cnt
        while cnt > 0:
            x, y = rnd.randint(self.wd * 0.05, self.wd), rnd.randint(self.ht * 0.15, self.ht)
            w, h = rnd.randint(1, self.wd * 0.7), rnd.randint(1, self.ht * 0.7)
            new_wall = Wall(x, y, w, h)
            intersects = False
            if not with_intersection:
                for wall in self.walls:
                    if wall.is_intersects(new_wall) or wall.is_intersects(self.rooms[0]):
                        intersects = True
                        break

            if not intersects:
                self.walls.append(new_wall)
                cnt -= 1

        for wall in self.walls:
            self.create_wall(wall)

    def free_all_cells(self):
        for cells in self.cells:
            for cell in cells:
                cell.unblock()

    def is_cell_blocked(self, x, y):
        if 0 < x < self.wd - 1 and 0 < y < self.ht - 1:
            return self.cells[x][y].is_blocked
        return True
