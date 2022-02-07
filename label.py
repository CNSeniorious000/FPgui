from base import *
from magic import *
from config import *
from typing import Any


class Label(pg.sprite.Sprite):
    pass


class Monitor(pg.sprite.Sprite):
    def __init__(
            self,
            entity: Any,
            anchor: tuple[int,int],

            align: Align = Align.center,
            render_group: pg.sprite.RenderUpdates = None,
            font_size: int = text_size,
            font_color: tuple = black,
            font_path: str = font,
            cache: bool = True,
            subpixel: bool = True
    ):
        self.last = self.image = self.rect = None
        pg.sprite.Sprite.__init__(self)
        self.entity = entity

        self.anchor = anchor
        self.align = align

        self.render_group = get_render_group() if render_group is None else render_group

        self.font_size = font_size
        self.font_color = font_color
        self.font_path = font_path

        self.subpixel = subpixel

        def get_surface(this):
            return paint_PIL(
                str(this), self.font_color, self.font_path, self.font_size,
                {1:"left", 2:"center", 4:"right"}[self.align >> 3]
            )
        if cache:
            get_surface.__name__ += f"{align}{font_size}{font_color}{font_path}"
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
            self.group.remove(self)
        else:
            self.last = this
            self.group.add(self)

            self.image = surface = self.get_surface(str(this))
            self.rect = locate(surface.get_rect(), self.align, self.anchor)

    def __repr__(self):
        return f"Monitor(entity={self.entity})"
