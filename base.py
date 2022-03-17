import os, enum, ctypes, win32api
os.environ['NUMBA_NUM_THREADS'] = '1'  # disable multiprocessing
os.environ['SDL_VIDEO_CENTERED'] = '1'  # enable first centering
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # disable ad
os.environ['PYGAME_BLEND_ALPHA_SDL2'] = '1'  # enable blend
ctypes.windll.user32.SetProcessDPIAware(2)
SF = ctypes.windll.shcore.GetScaleFactorForDevice(0)
DSIZE = list(map(win32api.GetSystemMetrics, (0,1)))



class Align(enum.IntFlag):
    min_y = top    = enum.auto()
    mid_y =          enum.auto()
    max_y = bottom = enum.auto()
    min_x = left   = enum.auto()
    mid_x =          enum.auto()
    max_x = right  = enum.auto()

    mid_top      = mid_x | min_y  # 中上
    mid_bottom   = mid_x | max_y  # 中下
    mid_left     = min_x | mid_y  # 中左
    mid_right    = max_x | mid_y  # 中右
    center       = mid_x | mid_y  # 中央
    top_left     = min_x | min_y  # 左上
    top_right    = max_x | min_y  # 左右
    bottom_left  = min_x | max_y  # 左下
    bottom_right = max_x | max_y  # 右下


def locate(rect, align:Align, anchor):
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
    scene_changed = enum.auto()
    break_loop = enum.auto()


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
