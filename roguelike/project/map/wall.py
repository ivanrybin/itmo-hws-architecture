"""
    Wall реализация стены.
"""


from map.rectangle import Rectangle


class Wall(Rectangle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
