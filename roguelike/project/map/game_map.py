"""
    Map реализует игровую карту.
"""

from map.cell import Cell
from map.room import Room
from map.wall import Wall

from logic.states import State

import random as rnd


class Map:
    def __init__(self, width, height, player_start_x, player_start_y, dungeon=False, load_type='NORMAL'):
        self.wd = width
        self.ht = height
        self.px = player_start_x
        self.py = player_start_y
        self.dungeon = dungeon
        self.walls = []
        self.start_room = Room(self.px - 5, self.py - 5, 10, 10)
        self.rooms = [self.start_room]
        if load_type == 'LOAD':
            return
        self.cells = self.__init_cells()
        self.state = State.PLAYER_TURN

    def __init_cells(self):
        cells = [[Cell(self.dungeon) for y in range(self.ht)] for x in range(self.wd)]
        return cells

    def create_wall(self, wall):
        for x in range(max(0, min(wall.x1, self.wd)), max(0, min(wall.x2, self.wd))):
            for y in range(max(0, min(wall.y1, self.ht)), max(0, min(wall.y2, self.ht))):
                self.cells[x][y].block()

    def create_room(self, room):
        if self.dungeon:
            for x in range(max(0, min(room.x1, self.wd)), max(0, min(room.x2, self.wd))):
                for y in range(max(0, min(room.y1, self.ht)), max(0, min(room.y2, self.ht))):
                    self.cells[x][y].unblock()

    def create_rooms(self, cnt=rnd.randint(5, 10), with_intersection=False):
        if not self.dungeon:
            return

        while cnt > 0:
            x, y = rnd.randint(1, self.wd), rnd.randint(3, self.ht)
            w, h = rnd.randint(3, self.wd * 0.7), rnd.randint(3, self.ht * 0.7)
            new_room = Room(x, y, w, h)
            intersects = False
            if not with_intersection:
                for room in self.rooms:
                    if room.is_intersects(new_room):
                        intersects = True
                        break

            if not intersects:
                self.rooms.append(new_room)
                cnt -= 1

        for room in self.rooms:
            self.create_room(room)

    def create_walls(self, cnt=rnd.randint(5, 10), with_intersection=False):
        if self.dungeon:
            return

        while cnt > 0:
            x, y = rnd.randint(self.wd * 0.05, self.wd), rnd.randint(self.ht * 0.15, self.ht)
            w, h = rnd.randint(1, self.wd * 0.7), rnd.randint(1, self.ht * 0.7)
            new_wall = Wall(x, y, w, h)
            intersects = False
            if not with_intersection:
                for wall in self.walls:
                    if wall.is_intersects(new_wall) or wall.is_intersects(self.start_room):
                        intersects = True
                        break

            if not intersects:
                self.walls.append(new_wall)
                cnt -= 1

        for wall in self.walls:
            self.create_wall(wall)

    def free_cells(self, to_free):
        for x, y in to_free:
            self.cells[x][y].unblock()

    def block_cells(self, to_block):
        for x, y in to_block:
            self.cells[x][y].block()

    def is_cell_blocked(self, x, y):
        if 0 < x < self.wd - 1 and 0 < y < self.ht - 1:
            return self.cells[x][y].is_blocked
        return True
