class Cell:
    def __init__(self, is_blocked, is_discovered=None):
        self.is_blocked = is_blocked

        if is_discovered is None:
            is_discovered = is_blocked

        self.is_discovered = is_discovered

    def block(self):
        self.is_blocked = True
        self.is_discovered = False

    def unblock(self):
        self.is_blocked = False
        self.is_discovered = True
