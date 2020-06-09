from engine.engine import starter

if __name__ == '__main__':
    game = starter(default=True, dungeon=False, debug=False)
    game.run()



