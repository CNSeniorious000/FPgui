from . import *
from collections import deque
import numpy as np



class Window:
    """cached scene or sub window"""
    current: "Window" = None

    def __init__(self, x, y, bgd=None):
        self.size = [scaled(x), scaled(y)]
        self.shown = False
        buffer = pg.Surface(self.size)
        match bgd:
            case pg.Surface(): buffer.blit(bgd, (0, 0))
            case np.ndarray(ndim=3): pg.surfarray.blit_array(buffer, bgd)
            case tuple() | list() | str(): buffer.fill(bgd)
            case int(): pg.surfarray.pixels3d(buffer)[:] = bgd
            case None: pass
            case _: raise TypeError(f"{type(bgd) = }")
        self.canvas = self.bgd = buffer.convert()

        self.widgets = deque()
        self.queue = deque()
        self.logic_group = pg.sprite.Group()
        self.render_group = pg.sprite.RenderUpdates()

    def __repr__(self):
        return "Window(size={}x{}, shown={})".format(*self.size, self.shown)

    @property
    def on_scene(self):
        return Window.current is self
