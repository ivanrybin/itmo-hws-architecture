"""
    MessageLog реализует логирование игровых событий для их последующего вывода.
"""

import tcod as tc
import textwrap as tw


class Message:
    def __init__(self, text, color=tc.white):
        self.txt = text
        self.color = color


class OperationLog:
    def __init__(self, lst_log=None):
        if lst_log is None:
            lst_log = []
        self.log = lst_log

    def add_item(self, item):
        self.log.append(item)


class MessageLog:
    def __init__(self, x, width, height):
        self.msgs = []
        self.x = x
        self.wd = width
        self.ht = height

    def add_message(self, message):
        new_msg_lines = tw.wrap(message.txt, self.wd)

        for line in new_msg_lines:
            if len(self.msgs) == self.ht:
                del self.msgs[0]

            self.msgs.append(Message(line, message.color))
