from magic import *
from names import *
import pygame as pg
from typing import Callable, Sequence, Dict, Tuple, Optional
from collections import deque


class ButtonBase(pg.sprite.Sprite):
    def __init__(
            self,
            group: pg.sprite.RenderUpdates = None,  # render set
            queue: deque = None,  # invoke queue
            callback: Optional[Callable] = None,  # function
            args: Optional[Tuple] = None,  # position arguments
            kwargs: Optional[Dict] = None  # keyword arguments
    ):
        assert callable(callback) or callback is None

        pg.sprite.Sprite.__init__(self)
        self.group = group
        self.queue = queue
        self.callback = [callback] if callback is not None else []
        self.argument = [(() if args is None else args, {} if kwargs is None else kwargs)]

        self.non_plateau = False
        self._situation = Situation.standby

    def __call__(self, function: Callable):
        """use as decorator"""
        assert callable(function)
        self.callback.append(function)
        if len(self.callback) > len(self.argument):
            self.argument.append(((), {}))
        return function

    def bind(self, *args, **kwargs):
        assert len(self.callback) == len(self.argument)
        self.argument.append((args, kwargs))
        return self

    @property
    def dirty(self):
        return self.non_plateau

    @dirty.setter
    def dirty(self, non_plateau):
        """will determine whether to draw itself"""
        if non_plateau:
            self.non_plateau = True
            self.group.add(self)
        else:
            self.non_plateau = False
            self.group.remove(self)

    @property
    def situation(self):
        return self._situation

    @situation.setter
    def situation(self, situation):
        self._situation = situation
        self.dirty = True
        if situation == Situation.clicked:
            self.queue.append(self.callback)
            self._situation = Situation.clicked


class Pushbutton(ButtonBase):
    def __init__(
            self, rect=None, render=None, queue=None, callback=None,
            text: str = "×",
            fg_color: Sequence = (179, 55, 55),
            t_color: Sequence = (255, 255, 255),
            font_path: str = "./resources/JetBrains Mono NL Light.ttf",
            font_size: int = 18,
            radius=10.5,
            luma_map: Sequence = (1, 0.8, 0.5, 0),
            speed_map: Sequence = (0.23, 0.23, 0.5)
    ):

        ButtonBase.__init__(self, rect, render, queue, callback)
        self.fg_c = np.array(fg_color) / 255
        self.t_c = np.array(t_color) / 255
        self.radius = radius
        self.luma_map = luma_map
        self.speed_map = speed_map

        self.now = luma_map[-1]
        self.text_bbox = self.text_alpha = None
        self.meta = (text, fg_color, t_color, font_path, font_size)

    @property
    def image(self):
        return self.get_surface(self.text)

    @staticmethod
    @memoize
    def get_surface():

    def setup(self):
        rect = self._rect
        radius = self.radius
        text, fg_color, t_color, font_path, font_size = self.meta

        self.dirty = True

        try:
            self.text_bbox = txtButton.cache[rect.size, text, font_path, font_size]
            self.text_alpha = txtButton.cache[text, t_color, font_path, font_size]
            try:
                self.cache = txtButton.cache[rect.size, text, fg_color, t_color, font_path, font_size, radius]
                self.draw()
                return  # only chance to avoid recreation of self.cache
            except KeyError:
                pass

        except KeyError:
            # print(f"{text!r} {self.rect} 在创建时啥也没缓存到")
            t_w, t_h = pg.font.Font(font_path, font_size).render(text, False, 0, 0).get_size()
            t_x = (self._rect.w - t_w) // 2
            t_y = (self._rect.h - t_h) // 2
            self.text_bbox = txtButton.cache[rect.size, text, font_path, font_size] = (t_x, t_y, t_w, t_h)
            self.text_alpha = txtButton.cache[text, t_color, font_path, font_size] \
                = paintln_FP(text, font_path, font_size, (t_w, t_h), 1, self.t_c)
        self.cache = txtButton.cache[rect.size, text, fg_color, t_color, font_path, font_size, radius] = {}

        self.draw()

    def draw(self):
        """refresh self.image"""
        """在这里定义如何重绘除文字外的内容"""
        """以及如何利用cache"""
        try:
            self.image = self.cache[self.now // 0.00390625]
            print("|", end="", flush=True)
        except KeyError:
            print("/", end="", flush=True)
            fg_c = self.fg_c * self.now
            w, h = self._rect.size
            surfarray = np.tile(fg_c, w * h).reshape((w, h, 3))
            try:
                surface = self.image.copy()  # with alpha channel tailed
            except AttributeError:
                surface = pg.Surface(self._rect.size, pg.SRCALPHA)
                surface.fill("#ffffff")
                tailor(pg.surfarray.pixels_alpha(surface), self.radius)
            remix_FP(self.text_alpha, self.t_c, surfarray, self.text_bbox)
            pg.surfarray.pixels3d(surface)[:] = surfarray * 255
            self.image = self.cache[self.now // 0.00390625] = surface.convert_alpha()

    def resize(self, *bbox, flush=True):
        self.image = None
        self._rect.update(*bbox)
        if flush:
            self.setup()
        else:
            assert not self.dirty  # avoid useless blit

    def update(self):
        if self.non_plateau:
            target_ratio = self.luma_map[self._situation]
            if abs(delta := target_ratio - self.now) < 0.00390625:
                self.dirty = False
                return

            self.now += delta * self.speed_map[self._situation]
            self.draw()
