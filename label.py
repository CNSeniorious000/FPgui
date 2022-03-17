from base import *
from magic import *
from window import *
from config import *
from typing import Any


class Label(pg.sprite.Sprite):
    def __init__(self,
            text: Any,
            anchor: tuple[int,int],
            align: Align = Align.center,
            font_size: int = text_size,
            font_color: tuple = black,
            font_path: str = font,
            subpixel: bool = True,
            window: Window | None = None
    ):
        self.image = self.rect = None
        self.window = window or Window.current
        pg.sprite.Sprite.__init__(self, self.window.logic_group)
        self.text = text
        self.anchor = anchor
        self.align = align
        self.font_size = font_size
        self.font_color = font_color
        self.font_path = font_path
        self.subpixel = subpixel

        self.shown = False

    def update(self):
        if self.shown:
            self.kill()  # commit suicide
        else:
            self.image = surface = paint_PIL(
                str(self.text), self.font_color, self.font_path, self.font_size,
                {1:"left", 2:"center", 4:"right"}[self.align >> 3]
            )
            self.rect = locate(surface.get_rect(), self.align, self.anchor)
            self.shown = True
            self.window.render_group.add(self)


class Monitor(pg.sprite.Sprite):
    def __init__(
            self,
            entity: Any,

            anchor: tuple[int,int],
            align: Align = Align.center,

            font_size: int = text_size,
            font_color: tuple = black,
            font_path: str = font,

            subpixel: bool = True,
            cache: bool = True,

            window: Window | None = None,
    ):
        self.last = self.image = self.rect = None
        self.window = window or Window.current
        pg.sprite.Sprite.__init__(self, self.window.logic_group)

        self.entity = entity

        self.anchor = anchor
        self.align = align

        self.font_size = font_size
        self.font_color = font_color
        self.font_path = font_path

        self.subpixel = subpixel

        def get_surface(string):
            return paint_PIL(
                string, self.font_color, self.font_path, self.font_size,
                {1:"left", 2:"center", 4:"right"}[self.align >> 3]
            )
        if cache:
            get_surface.__name__ += f"-{align}-{font_size}-{font_color}-{font_path}"
            self.get_surface = memoize_surfaces(get_surface)
        else:
            self.get_surface = get_surface


    def update(self):
        entity = self.entity
        if callable(entity):
            this = entity()
        elif isinstance(entity, str):
            this = eval(entity)
        else:
            this = repr(entity)

        if this == self.last:
            self.window.render_group.remove(self)
        else:
            self.last = this
            self.window.render_group.add(self)

            self.image = surface = self.get_surface(str(this))
            self.rect = locate(surface.get_rect(), self.align, self.anchor)

    def __repr__(self):
        return f"Monitor(entity={self.entity})"
