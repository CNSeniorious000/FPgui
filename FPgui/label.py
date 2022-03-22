from . import *
from .magic import *
from .config import *
from functools import cached_property
from autoprop import autoprop
from loguru import logger


class Label(Being):
    def __init__(
            self,
            anchor: tuple[int,int] = (None, None),
            align: Align = Align.center,
            font_size: int = text_size,
            font_color: tuple = black,
            font_path: str = font,
            subpixel: bool = True,
    ):
        Being.__init__(self, None, None, *scaled(anchor), align)
        self.font_size = scaled(font_size)
        self.font_color = font_color
        self.font_path = font_path
        self.subpixel = subpixel  # useless for now

    def draw(self, text):
        return (surface := paint_PIL(
            str(text), self.font_color, self.font_path, self.font_size, self.align_v
        )), self.get_bbox(surface)


class StaticText(Label):
    def __init__(self, text, *args, **kwargs):
        self.text = text
        self.shown = False
        Label.__init__(self, *args, **kwargs)

    def __repr__(self):
        return f"Label(text={self.text!r})"

    def update(self):
        if self.shown:
            self.dirty = False
        else:
            self.shown = self.dirty = True

    @cached_property
    def surfs(self):
        return [self.draw(self.text)]


@autoprop
class Monitor(Label):
    def __init__(self, entity, *args, cache=True, **kwargs):
        self.entity = entity
        self.last = None
        self.surfs = []
        Label.__init__(self, *args, **kwargs)
        self.get_surface = paint_PIL
        self.cache = cache

    def __repr__(self):
        return f"Monitor(entity={self.entity!r})"

    @cached_property
    def bgd(self) -> pg.Surface:
        return self.root.bgd

    @staticmethod
    @memoize_surfaces
    def _get_surface_cached(text, font_color, font_path, font_size, align_v):
        return paint_PIL(text, font_color, font_path, font_size, align_v)

    def get_cache(self):
        return isinstance(self.get_surface, memoize_surfaces)

    def set_cache(self, cache):
        match cache:
            case False:
                self.get_surface = self._get_surface_cached.raw
            case True:
                self.get_surface = self._get_surface_cached
            case str():
                memoize_surfaces.load(cache, self._get_surface_cached.__name__)

    def del_cache(self):
        self._get_surface_cached.data.clear()

    def draw(self, text) -> tuple[pg.Surface, pg.Rect]:
        return (surface := self.get_surface(
            text, self.font_color, self.font_path, self.font_size, self.align_v
        )), self.get_bbox(surface)

    def update(self):
        entity = self.entity
        if callable(entity):
            this = entity()
        elif isinstance(entity, str):
            this = eval(entity)
        else:
            this = repr(entity)

        if this == self.last:
            self.dirty = False
        else:
            self.dirty = True
            self.last = this
            this_surf, this_rect = self.draw(str(this))

            try:
                last_rect: pg.Rect = self.surfs[-1][1]
                self.surfs.clear()
                self.surfs.append((self.bgd, last_rect, last_rect))
            except IndexError:
                pass  # first time
            self.surfs.append((this_surf, this_rect))
