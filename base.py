import enum


class Align(enum.Flag):
    min_x = left   = enum.auto()
    mid_x =          enum.auto()
    max_x = right  = enum.auto()
    min_y = top    = enum.auto()
    mid_y =          enum.auto()
    max_y = bottom = enum.auto()

    mid_top      = mid_x | min_y  # 中上
    mid_bottom   = mid_x | max_y  # 中下
    mid_left     = min_x | mid_y  # 中左
    mid_right    = max_x | mid_y  # 中右
    center       = mid_x | mid_y  # 中央
    left_top     = min_x | min_y  # 左上
    right_top    = max_x | min_y  # 左右
    bottom_left  = min_x | max_y  # 左下
    bottom_right = max_x | max_y  # 右下


class Situation(enum.IntEnum):
    standby = 0
    hovering = 1
    pressing = 2
    clicked = 3
    """光是released没有意义"""


class Action(enum.Flag):
    nothing = 0
    scene_change = enum.auto()
    break_loop = enum.auto()


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
