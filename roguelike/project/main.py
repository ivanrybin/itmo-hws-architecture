from engine.engine import starter

if __name__ == '__main__':
    game = starter(default_screen=True, dungeon=False, fov_mode=True, debug=False)
    game.run()



