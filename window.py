import os, ctypes, win32api
from collections import deque
import numpy as np
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
os.environ['SDL_VIDEO_CENTERED'] = '1'
SF = ctypes.windll.shcore.GetScaleFactorForDevice(0)
display_size = list(map(win32api.GetSystemMetrics, (0,1)))
import pygame as pg


def scaled(x):
    assert x % 4 == 0
    return x * SF // 100


class Window:
    """cached scene or sub window"""
    def __init__(self, x, y, bgd=None, shown=False):
        self.size = [x, y]
        self.shown = shown
        buffer = pg.Surface((x, y))
        match bgd:
            case pg.Surface(): buffer.blit(bgd, (0, 0))
            case np.ndarray(ndim=3): pg.surfarray.blit_array(buffer, bgd)
            case tuple() | list() | str(): buffer.fill(bgd)
            case int(): pg.surfarray.pixels3d(buffer)[:] = bgd
            case None: pass
            case _: raise TypeError(f"{type(bgd) = }")
        self.canvas = self.bgd = buffer  # .convert()

        self.widgets = deque()
        self.queue = deque()
        self.logic_group = pg.sprite.Group()
        self.render_group = pg.sprite.RenderUpdates()

    def __repr__(self):
        return "Frame(size={}x{}, shown={})".format(*self.size, self.shown)


