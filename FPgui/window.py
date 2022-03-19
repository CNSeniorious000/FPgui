from . import Align, scaled
from .layout import MinimizedContainer
from contextlib import contextmanager
from collections import deque
import numpy as np
import pygame as pg


class Window(MinimizedContainer):
    """cached scene or sub window"""
    current: "Window" = None

    def __init__(self, size, align=Align.center, anchor=(None,None), bgd=None):
        MinimizedContainer.__init__(self, *scaled(size), align, *scaled(anchor), window=self)
        buffer = pg.Surface(self.size)
        match bgd:
            case pg.Surface(): buffer.blit(bgd, (0, 0))
            case np.ndarray(ndim=3): pg.surfarray.blit_array(buffer, bgd)
            case tuple() | list() | str(): buffer.fill(bgd)
            case int(): pg.surfarray.pixels3d(buffer)[:] = bgd
            case None: pass
            case _: raise TypeError(f"{type(bgd) = }")
        self.canvas = self.bgd = buffer.convert()

        self.queue = deque()
        self.logic_group = pg.sprite.Group()
        self.render_group = pg.sprite.RenderUpdates()

    def __repr__(self):
        return "Window(size={}x{}, anchor=({},{}))".format(*self.size, *self.anchor)

    @contextmanager
    def using(self, relocation=True):
        from .ui import use, main_loop
        use(self, relocation)
        yield self.__enter__()
        main_loop()
        self.__exit__(None, None, None)

    def use(self, relocation=True):
        from .ui import use
        return use(self, relocation)

    def use_async(self, relocation=True):
        from .ui import use_async
        return use_async(self, relocation)
