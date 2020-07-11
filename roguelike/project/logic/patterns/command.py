"""
    Паттерн команда.

    Command - обертка над функцией и ее аргументами,
              имеет единственный метод execute,
              испольняющий вложенную в объект функцию,
              возвращающий ее результат.
"""


class Command:
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def execute(self):
        return self.func(*self.args, **self.kwargs)
