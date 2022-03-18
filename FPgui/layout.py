from . import *
from collections import deque


class MinimizedContainer(Widget):
    """basic layout widget"""

    def __init__(self, align, anchor, window=None, parent=None):
        Widget.__init__(self, align, *anchor, window, parent)
        self.children = deque()

    def __contains__(self, item):
        return item in self.children

    def __iter__(self):
        return iter(self.children)

    def check(self, recursive=False):
        if isinstance(self.parent, MinimizedContainer) and self in self.parent:
            return all(child.parent is self for child in self) if recursive else \
                all(child.check() for child in self)

    def add(self):
        pass

