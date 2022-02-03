from magic import *
from config import *
from typing import Any, Literal, Callable


class Label(pg.sprite.Sprite):
    pass


class Spyer(pg.sprite.Sprite):
    def __init__(
            self,
            group: pg.sprite.Group,
            entity: Any,
            anchor,
            align:Align = Align.center,
            size=text_size,
            color=black,
            font=font,
            subpixel=True
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
        return paint_PIL(str(self.last), self.color, self.font, self.size)

    def __repr__(self):
        return f"Spyer(last={self.last})"
