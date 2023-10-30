"""
This file hasn't been used,
but in the near future it'll be
refactored and put into use.
"""

from . import *
import numpy as np
import pygame as pg


class Image:
    def __init__(self, data: pg.Surface | np.ndarray, **meta):
        self.data = data
        self.meta = meta

        if isinstance(data, np.ndarray):
            shape = data.shape
            self.size = shape[1], shape[0]
            if data.ndim == 2:
                self.mode = "L"
            else:
                match shape[2]:
                    case 2: self.mode = "LA"
                    case 3: self.mode = "RGB"
                    case 4: self.mode = "RGBA"

        elif isinstance(data, pg.Surface):
            self.size = data.get_size()
            match data.get_bytesize():
                case 1: self.mode = "L"
                case 3: self.mode = "RGB"
                case 4: self.mode = "RGBA"

        else:
            raise TypeError(f"{data = }")


    @property
    def surf(self):
        data = self.data
        if isinstance(data, pg.Surface):
            return data
        elif isinstance(data, np.ndarray):
            _ = data.shape
            return pg.image.frombuffer(data, (_[1], _[0]), "RGBA"[:data.ndim+1])

    @property
    def arr(self):
        data = self.data
        if isinstance(data, np.ndarray):
            return data
        elif isinstance(data, pg.Surface):
            return np.asarray(data.get_buffer(), np.uint8).reshape(*data.get_size(), -1)

    def blit(self, source, dest, area=None, blend_mode=None):
        source: Image
        if isinstance(self.data, pg.Surface):
            match blend_mode:
                case Blend.add: flag = pg.BLEND_ADD
                case Blend.multiply: flag = pg.BLEND_MULT
                case _: flag = 0
            return self.data.blit(source.surf, dest, area, flag)
        else:
            x, y = dest[:2]
            w, h = area
