import tcod as tc
import random as rnd


class Entity:
    def __init__(self, x, y, screen_width, screen_height, char, color, game_map=None, strategy=None):
        self.x = x
        self.y = y
        self.sw = screen_width
        self.sh = screen_height
        if isinstance(char, int):
            self.char = char
        if isinstance(char, str):
            self.char = ord(char)
        self.color = color
        self.map = game_map
        self.strategy = strategy

    def update_pos(self, game_map):
        pass
