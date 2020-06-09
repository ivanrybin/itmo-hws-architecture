import tcod as tc
import random as rnd

class Entity:
    def __init__(self, x, y, screen_width, screen_height, char, color, game_map=None):
        self.x = x
        self.y = y
        self.char = ord(char)
        self.color = color
        self.sw = screen_width
        self.sh = screen_height
        self.map = game_map

    def update_pos(self, game_map):
        pass
