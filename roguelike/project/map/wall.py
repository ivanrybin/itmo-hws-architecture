"""
    Wall реализация стены.
"""


class Wall:
    def __init__(self, x, y, width, height):
        self.x1 = x
        self.x2 = x + width
        self.y1 = y
        self.y2 = y + height

    def is_intersects(self, other):
        return (other.x1 <= self.x1 <= other.x2 and
                other.y1 <= self.y1 <= other.y2) or \
               (other.x1 <= self.x2 <= other.x2 and
                other.y1 <= self.y2 <= other.y2)

    def is_point_in(self, x, y):
        return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2

    def serialize(self):
        data = {
            'x': self.x1,
            'y': self.y1,
            'width': self.x2 - self.x1,
            'height': self.y2 - self.y1,
        }

        return data
