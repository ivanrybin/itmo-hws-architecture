class Cell:
    def __init__(self, is_blocked, is_walk=None):
        self.is_blocked = is_blocked

        if is_walk is None:
            is_walk = is_blocked

        self.is_walk = is_walk

    def block(self):
        self.is_blocked = True
        self.is_walk = False

    def unblock(self):
        self.is_blocked = False
        self.is_walk = True
