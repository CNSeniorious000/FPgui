from . import *
import numpy as np, pygame as pg
from collections import deque
from contextlib import contextmanager


class Container(Widget):
    def __init__(self, *args, **kwargs):
        self.children = deque()
        Widget.__init__(self, *args, **kwargs)
        self.window: Window = self.root

    def resize(self):  # bottom up
        """宣称大小改变，向上找，直到找到一个size确定的，开始layout"""
        if (parent := self.parent) is None:
            return self.layout()
        else:
            assert isinstance(parent, Container)
            return parent.layout() if parent.fixed else parent.resize()

    def layout(self):  # top down
        return self.get_size()

    def render(self) -> list[list[pg.Rect]]:
        blits = self.window.canvas.blits
        return [
            blits(widget.surfs)
            for widget in self.children
            if isinstance(widget, Being) and widget.dirty
        ]

    def update(self, *args, **kwargs):
        return [widget.update(*args, **kwargs) for widget in self.children]

    def __contains__(self, item):
        return item in self.children

    def __len__(self):
        return len(self.children)

    def __iter__(self):
        return iter(self.children)

    def append(self, widget:Widget):
        return self.children.append(widget)

    def insert(self, index:int, widget:Widget):
        return self.children.insert(index, widget)

    def remove(self, widget:Widget):
        return self.children.remove(widget)

    def pop(self):
        return self.children.pop()

    def popleft(self):
        return self.children.popleft()

    def __enter__(self):
        from . import ui
        self.__tmp, ui.current_parent = ui.current_parent, self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        from . import ui
        ui.current_parent = self.__tmp
        del self.__tmp


class Window(Container):
    """cached scene or sub window"""
    current: "Window" = None

    def __init__(self, size, anchor=(None,None), align=Align.center, bgd=None):
        from . import ui  # to enable buffer.convert()
        buffer = pg.Surface(scaled_size := scaled(size))
        match bgd:
            case pg.Surface(): buffer.blit(bgd, (0, 0))
            case np.ndarray(ndim=3): pg.surfarray.blit_array(buffer, bgd)
            case tuple() | list() | str(): buffer.fill(bgd)
            case int(): pg.surfarray.pixels3d(buffer)[:] = bgd
            case None: pass
            case _: raise TypeError(f"{type(bgd) = }")
        self.canvas = self.bgd = buffer.convert()

        x, y = scaled(anchor)
        if align is Align.center:  # TODO: 应该让window.anchor和ui.anchor都非null. 改写 getter setter >>>
            W, H = DSIZE
            if x is None:
                x = W // 2
            if y is None:
                y = H // 2
        Container.__init__(self, *scaled_size, x, y, align)
        self.queue = deque()

    def __repr__(self):
        return "Window(size={}x{}, anchor=({},{}))".format(*self.size, *self.anchor)

    @property
    def root(self):
        return self

    def set_anchor(self, anchor):
        from . import ui
        self.x, self.y = anchor
        ui.anchor[:] = anchor
        ui.move_to(*anchor, self.align)

    def render(self):
        blits = self.canvas.blits
        return [
            blits(widget.surfs)
            for widget in self.children
            if isinstance(widget, Being) and widget.dirty
        ]

    @contextmanager
    def using(self, frames: int = None, *, relocation=True) -> "Window":
        from .ui import use, main_loop
        last = Window.current
        use(self, relocation)
        yield self.__enter__()
        main_loop(frames)
        use(last, relocation)
        self.__exit__(None, None, None)

    def use(self, *, relocation=True):
        from .ui import use
        return use(self, relocation)

    def use_async(self, frames: int = None, *, relocation=True):
        from .ui import use_async
        return use_async(self, frames, relocation)


class Box(Container):
    def __init__(self, *args, padding=None, spacing=None, **kwargs):
        self.margin = [0, 0, 0, 0]
        self.h_gap = self.v_gap = 0
        Container.__init__(*args, **kwargs)
        self.padding = padding
        self.spacing = spacing

    def get_padding(self):
        return self.margin

    def set_padding(self, padding):
        match padding:
            case int():
                self.margin[:] = padding
            case int(), int() as h, v:
                self.margin[:] = h, v
            case int(), int(), int(), int():
                self.margin[:] = padding
            case None:
                pass
            case _:
                raise ValueError(padding)

    def del_padding(self):
        self.margin[:] = 0

    padding: tuple[int,int,int,int] = property(
        lambda self: self.get_padding(),
        lambda self, padding: self.set_padding(padding),
        lambda self: self.del_padding()
    )

    def get_spacing(self):
        return self.h_gap, self.v_gap

    def set_spacing(self, spacing):
        match spacing:
            case int():
                self.h_gap = self.v_gap = spacing
            case int(), int() as h, v:
                self.h_gap, self.v_gap = h, v
            case None:
                pass
            case _:
                raise ValueError(spacing)

    def del_spacing(self):
        self.h_gap = self.v_gap = 0

    spacing: tuple[int,int] = property(
        lambda self: self.get_spacing(),
        lambda self, spacing: self.set_spacing(spacing),
        lambda self: self.del_spacing()
    )


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
