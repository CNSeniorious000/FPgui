from . import *
from collections import deque


class Container(Widget):
    """basic layout widget"""

    def __init__(self, *args, margin=0, spacing=0, **kwargs):
        Widget.__init__(self, *args, **kwargs)
        self.children = deque()
        match margin:
            case int():
                self.left = self.right = self.up = self.down = margin
            case (horizontal, vertical):
                self.left = self.right = horizontal
                self.up = self.down = vertical
            case (a, b, c, d):
                self.left, self.right, self.up, self.down = a, b, c, d
            case _:
                raise ValueError(margin)
        match spacing:
            case int():
                self.h_gap = self.v_gap = spacing
            case (horizontal, vertical):
                self.h_gap, self.v_gap = horizontal, vertical
            case _:
                raise ValueError(spacing)

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

    def append(self, widget: Widget):
        assert isinstance(widget, Widget) and widget not in self
        return self.children.append(widget)

    def insert(self, index, widget: Widget):
        assert isinstance(widget, Widget) and widget not in self
        return self.children.insert(index, widget)

    def pop(self):
        return self.children.pop()

    def popleft(self):
        return self.children.popleft()

    @staticmethod
    def resize():
        return NotImplemented


class VBox(Container):
    def do_fit(self):
        ...

    def append(self, widget: Widget):
        ...

    def insert(self, index, widget: Widget):
        ...

class HBox(Container):
    def do_fit(self):
        ...

    def append(self, widget: Widget):
        ...

    def insert(self, index, widget: Widget):
        ...
