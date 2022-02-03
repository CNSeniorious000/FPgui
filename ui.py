from curses.ascii import SI
from itertools import count
from window import *
from button import *
from loguru import logger


clock = pg.time.Clock()
flags = pg.NOFRAME
size = []
screen = pg.display.set_mode(flags=pg.HIDDEN)  # to enable convert()
scene: Window = None
hovering = pressed = None
num = 0


def switch_to(window:Window):
    global screen, scene

    if scene is not None:
        scene.shown = False
        scene.canvas = scene.canvas.copy()
    scene = window

    if window is None:
        screen = pg.display.set_mode(size, flags | pg.HIDDEN)
        return size.clear()

    if window.size != size:
        size[:] = window.size
        screen = pg.display.set_mode(size, flags | pg.SHOWN, vsync=True)
    window.canvas = screen
    window.shown = True

    return Action.scene_change

def center():
    hWnd = pg.display.get_wm_info()["window"]
    X, Y = display_size
    x, y = size
    ctypes.windll.user32.MoveWindow(hWnd, (X-x)//2, (Y-y)//2, x, y, False)

def use(window:Window, centering=True):
    if window is scene:
        return logger.warning(f"<{window = }> on scene.")
    switch_to(window)

    if centering:
        center()

    pg.display.flip()

    return Action.scene_change

def hide(clear=True):
    if clear:
        scene.queue.clear()
    use(None)

    return Action.break_loop

def parse_mouse_pos(pos):
    global hovering
    for widget in scene.logic_group:
        widget: pg.sprite.Sprite
        try:
            rect = widget.rect
        except AttributeError:
            continue

        if rect.collidepoint(pos):
            if widget is hovering:
                return

            # change hovering
            if hovering is not None:
                hovering.situation = Situation.standby
            if widget is pressed:  # 被按过 => 正被按
                widget.situation = Situation.pressing
            else:
                widget.situation = Situation.hovering
            hovering = widget
            return  # 不return的话可能有多个hovering
    else:
        if hovering is not None:
            hovering.situation = Situation.standby
            hovering = None

def parse_events(events):
    

def on_lose_focus():
    global hovering, pressed
    if hovering is not None:
        hovering.situation = Situation.standby
        hovering = None
    if pressed is not None:
        pressed.situation = Situation.standby
        pressed = None



def main_loop():
    global num
    logic_group = scene.logic_group
    render_group = scene.render_group
    queue = scene.queue

    for num in count(num):
        if pg.mouse.get_focused():
            parse_mouse_pos(pg.mouse.get_pos())
        else:
            on_lose_focus()
