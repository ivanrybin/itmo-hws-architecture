"""
    Wall -- реализация объекта, который может быть либо стеной либо комнатой.
"""


class Wall:
    def __init__(self, x, y, width, height):
        self.x_left = x
        self.x_right = x + width
        self.y_bottom = y
        self.y_top = y + height

    def is_intersects(self, other):
        return (other.x_left <= self.x_left <= other.x_right and
                other.y_bottom <= self.y_bottom <= other.y_top) or \
               (other.x_left <= self.x_right <= other.x_right and
                other.y_bottom <= self.y_top <= other.y_top)

    def is_point_in(self, x, y):
        return self.x_left <= x <= self.x_right and self.y_bottom <= y <= self.y_top

    def serialize(self):
        data = {
            'x': self.x_left,
            'y': self.y_top,
            'width': self.x_right - self.x_left,
            'height': self.y_top - self.y_bottom,
        }

        return data
