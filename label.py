from magic import *
from base import *
from config import *
from typing import Any


class Label(pg.sprite.Sprite):
    pass


class Monitor(pg.sprite.Sprite):
    def __init__(
            self,
            group: pg.sprite.Group,
            entity: Any,
            anchor: tuple[int,int],
            align: Align = Align.center,
            size: int = text_size,
            color: tuple = black,
            font: str = font,
            subpixel: bool = True
    ):
        self.last = None
        pg.sprite.Sprite.__init__(self, group)
        self.anchor = anchor
        self.align = align
        self.size = size
        self.color = color
        self.font = font
        self.subpixel = subpixel

        def updater(*_, **__):
            if callable(entity):
                this = entity()
            elif isinstance(entity, str):
                this = eval(entity)
            else:
                this = repr(entity)

            if this == self.last:
                group.remove(self)
            else:
                self.last = this
                group.add(self)

        self.update = updater

    @property
    def image(self):
        surface: pg.Surface = paint_PIL(str(self.last), self.color, self.font, self.size)
        self.rect = locate(surface.get_rect(), self.align, self.anchor)
        return surface

    def __repr__(self):
        return f"Monitor(last={self.last})"
