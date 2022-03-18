from . import *
from .magic import *
from .config import *
from typing import Any


class Label(Widget, pg.sprite.Sprite):
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
        Widget.__init__(self, align, *anchor, window)
        pg.sprite.Sprite.__init__(self, self.window.logic_group)
        self.image = self.rect = None
        self.text = text
        self.anchor = tuple(map(scaled, anchor))
        self.align = align
        self.font_size = scaled(font_size)
        self.font_color = font_color
        self.font_path = font_path
        self.subpixel = subpixel

        self.shown = False

    def update(self):
        if self.shown:
            self.kill()  # commit suicide
        else:
            self.image = surface = paint_PIL(
                str(self.text), self.font_color, self.font_path, self.font_size, self.align_v
            )
            self.rect = self.get_rect(surface)
            self.shown = True
            self.window.render_group.add(self)


class Monitor(Widget, pg.sprite.Sprite):
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
        Widget.__init__(self, align, *anchor, window)
        pg.sprite.Sprite.__init__(self, self.window.logic_group)

        self.last = self.image = self.rect = None
        self.entity = entity

        self.font_size = font_size = scaled(font_size)
        self.font_color = font_color
        self.font_path = font_path
        self.subpixel = subpixel

        def get_surface(string):
            return paint_PIL(
                string, self.font_color, self.font_path, self.font_size, self.align_v
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
            self.rect = self.get_rect(surface)

    def __repr__(self):
        return f"Monitor(entity={self.entity})"
