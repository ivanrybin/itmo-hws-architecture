class Cell:
    def __init__(self, is_blocked, id_discovered=None):
        self.is_blocked = is_blocked

        if id_discovered is None:
            id_discovered = is_blocked

        self.id_discovered = id_discovered

    def block(self):
        self.is_blocked = True
        self.id_discovered = False

    def unblock(self):
        self.is_blocked = False
        self.id_discovered = True
