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

    def __enter__(self):
        from . import ui
        self.__tmp, ui.current_parent = ui.current_parent, self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        from . import ui
        ui.current_parent = self.__tmp
        del self.__tmp

    def check(self, recursive=False):
        return all(child.check() for child in self) if recursive else \
            all(child.parent is self for child in self)

    def append(self, widget:Widget):
        assert isinstance(widget, Widget)
        self.children.append(widget)
