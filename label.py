from base import *
from magic import *
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
            cache: bool = True,
            subpixel: bool = True
    ):
        self.last = None
        pg.sprite.Sprite.__init__(self, group)
        self.group = group
        self.entity = entity
        self.anchor = anchor
        self.align = align
        self.size = size
        self.color = color
        self.font = font
        self.subpixel = subpixel

        _ = lambda string: paint_PIL(
            str(string), self.color, self.font, self.size,
            {1:"left", 2:"center", 4:"right"}[self.align >> 3]
        )
        self.get_surface = memoize_surfaces(_) if cache else _
        # 留下了重名碰撞缓存的隐患!!

        self.image = None
        self.rect = pg.Rect(*anchor, 0, 0)

    def update(self):
        entity = self.entity
        if callable(entity):
            this = entity()
        elif isinstance(entity, str):
            this = eval(entity)
        else:
            this = repr(entity)

        if this == self.last:
            self.group.remove(self)
        else:
            self.last = this
            self.group.add(self)

            self.image = surface = self.get_surface(str(this))
            self.rect = locate(surface.get_rect(), self.align, self.anchor)

    def __repr__(self):
        return f"Monitor(entity={self.entity})"
