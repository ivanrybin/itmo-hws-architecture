"""
    Запуск игры.
    Опции лучше не трогать.
"""
from game_starter import starter

if __name__ == '__main__':
    game = starter(default_screen=True, fov_mode=False, debug=False)
    game.run()
