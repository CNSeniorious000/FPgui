import enum, ctypes, win32api
from os import environ
from functools import cached_property
from contextlib import contextmanager

environ.update(  # maybe loaded from a config file in the future
    {
        'NUMBA_NUM_THREADS': '1',  # disable multiprocessing
        'SDL_VIDEO_CENTERED': '1',  # enable first centering
        'PYGAME_BLEND_ALPHA_SDL2': '1',  # enable blend
        'PYGAME_HIDE_SUPPORT_PROMPT': '1'  # disable ads
    }
)

ctypes.windll.user32.SetProcessDPIAware(2)
SF = ctypes.windll.shcore.GetScaleFactorForDevice(0)
DSIZE = list(map(win32api.GetSystemMetrics, (0, 1)))


def scaled(val):
    if SF:
        try:
            assert val is None or val % 4 == 0
            return val and val * SF // 100
        except TypeError:
            return [v and v * SF // 100 for v in val]
    else:
        return val


@contextmanager
def scaling_at(factor):
    global SF
    SF, factor = factor, SF
    yield SF
    SF = factor


class Align(enum.IntFlag):
    min_y = top    = 0b000001
    mid_y =          0b000010
    max_y = bottom = 0b000100
    min_x = left   = 0b001000
    mid_x =          0b010000
    max_x = right  = 0b100000

    mid_top      = mid_x | min_y  # 中上
    mid_bottom   = mid_x | max_y  # 中下
    mid_left     = min_x | mid_y  # 中左
    mid_right    = max_x | mid_y  # 中右
    center       = mid_x | mid_y  # 中央
    top_left     = min_x | min_y  # 左上
    top_right    = max_x | min_y  # 左右
    bottom_left  = min_x | max_y  # 左下
    bottom_right = max_x | max_y  # 右下

    @property
    def vertical(self):
        return self & 0b111

    @property
    def horizontal(self):
        return self & 0b111000

    def translate(self, x, y, w, h, to=top_left):
        import math
        dx = int(math.log2((to >> 3) / (self >> 3)) * w / 2)
        dy = int(math.log2((to & 0b111) / (self & 0b111)) * h / 2)
        return x + dx, y + dy

    @staticmethod
    def normalize(x, y, W, H):
        """get positive x and y"""
        return x and x % W, y and y % H


def locate(rect, align: Align, anchor):
    match align:
        case Align.top_left: rect.topleft = anchor
        case Align.mid_top: rect.midtop = anchor
        case Align.top_right: rect.topright = anchor
        case Align.mid_left: rect.midleft = anchor
        case Align.center: rect.center = anchor
        case Align.mid_right: rect.midright = anchor
        case Align.bottom_left: rect.bottomleft = anchor
        case Align.mid_bottom: rect.midbottom = anchor
        case Align.bottom_right: rect.bottomright = anchor
    return rect


class Situation(enum.IntEnum):
    standby = 0
    hovering = 1
    pressing = 2
    clicked = 3
    """光是released没有意义"""


class Action(enum.Flag):
    nothing = 0
    scene_changed = 1
    break_loop = 2


class Strategy(enum.IntEnum):
    each = 0
    union = 1
    whole = 2


class Blend(enum.Enum):
    """several blend mode"""
    "-> 更暗 <-"
    darken = "变暗"  # min(a, b)
    multiply = "正片叠底"  # a * b
    color_burn = "颜色加深"  # 1 - (1-b)/a
    linear_burn = "线性加深"  # a + b - 1 = a - (1-b)
    darker = "深色"  # min(a[], b[])
    # Luminance = sum(0.2126r + 0.7152g + 0.0722b)

    "-> 更亮 <-"
    lighten = "变亮"  # max(a, b)
    screen = "滤色"  # 1 - (1-a)(1-b)
    color_dodge = "颜色减淡"  # b/(1-a)
    add = "添加"  # a + b
    lighter = "浅色"  # max(a[], b[])

    "-> 对比 <-"
    overlay = "叠加"
    # a < 0.5 -> 2ab === 正片叠底
    # a = 0.5 -> b
    # a > 0.5 -> 1 - 2(1-a)(1-b) === 滤色
    soft_light = "柔光"
    # b < 0.5 -> 2ab + (1-2b) * a**2
    # b = 0.5 -> a
    # b > 0.5 -> 2a(1-b) + (2b-1) * a**0.5
    hard_light = "强光"  # soft_light(b,a)
    linear_light = "线性光"  # b + 2a - 1
    pin_light = "点光"
    # a < 0.5 -> min(2a, b)
    # a = 0.5 -> b
    # a > 0.5 -> max(2(a-0.5), b)


# noinspection PyPropertyDefinition
class Rect:
    """physical concept of a widget"""

    def __init__(self, w: int, h: int, x: int, y: int, align: Align):
        self.w, self.h, self.x, self.y = w, h, x, y
        self.align = align

    def translate(self, to=Align.top_left):
        return self.align.translate(self.x, self.y, self.w, self.h, to)

    def set_align(self, align):
        self.align = align
        self.set_anchor(*self.translate(align))

    def get_size(self):
        return self.w, self.h

    def set_size(self, size):
        self.w, self.h = size

    def del_size(self):
        self.w = self.h = None

    size: tuple[int, int] = property(
        lambda self: self.get_size(),
        lambda self, size: self.set_size(size),
        lambda self: self.del_size()
    )

    def get_anchor(self):
        return self.x, self.y

    def set_anchor(self, anchor):
        self.x, self.y = anchor

    def del_anchor(self):
        self.x = self.y = None

    anchor: tuple[int, int] = property(
        lambda self: self.get_anchor(),
        lambda self, anchor: self.set_anchor(anchor),
        lambda self: self.del_anchor()
    )

    @property
    def fixed(self):
        return None not in self.get_size()

    def get_bbox(self, surface):
        assert self.x and self.y
        return locate(surface.get_rect(), self.align, (self.x, self.y))

    @property
    def align_v(self):
        return {1: "left", 2: "center", 4: "right"}[self.align >> 3]


class Node:
    """logical concept of a widget"""

    def __init__(self, parent: "Node" = None):
        from . import ui
        self.parent = parent or ui.current_parent
        try:
            self.parent = self
        except AttributeError:
            assert isinstance(self, ui.Window)

    @cached_property
    def root_window(self):
        try:
            return self.parent.root_window
        except AttributeError:
            return self

    @staticmethod
    def update(*args, **kwargs):
        return NotImplemented


class Widget(Rect, Node):
    """widget entity"""

    def __init__(self, w=None, h=None, x=None, y=None, align=Align.center, parent=None):
        Rect.__init__(self, w, h, x, y, align)
        Node.__init__(self, parent)

    def __repr__(self):
        return "Widget(size={}, anchor={}, parent={}, root={})".format(
            self.size, self.anchor, self.parent, self.root_window
        )


class Being(Widget):
    """
    widget that can be rendered

    - **dirty** : whether to rerender
    - **surfs** : the surface to render
    - **rects** : the position to render
    """

    def __init__(self, *args, **kwargs):
        Widget.__init__(self, *args, **kwargs)
        self.dirty = False
        self.surfs: list[tuple]
