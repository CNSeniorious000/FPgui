from . import *
from .window import *
from itertools import count
from functools import wraps
from loguru import logger
import threading


flags = pg.NOFRAME
size = []  # last window's size
anchor = [None, None]  # last window's anchor
screen = pg.display.set_mode((1,1), flags=pg.HIDDEN)  # to enable convert()
hovering = pressed = None
current_parent: "MinimizedContainer" = None


@wraps(pg.display.set_mode)
def _reset_video_system(*args, **kwargs):
    if threading.current_thread().name != 'MainThread':
        pg.display.quit()
        pg.display.init()
        logger.success(threading.current_thread())
    # switching to MainThread from others doesn't cause DeadLock
    return pg.display.set_mode(*args, **kwargs)

def relocate():
    hWnd = pg.display.get_wm_info()["window"]
    scene = Window.current
    W, H = DSIZE
    w, h = size
    X, Y = anchor
    x, y = scene.align.translate_to_top_left(*scene.anchor, w, h)
    ctypes.windll.user32.MoveWindow(
        hWnd, x or X or (W - w) // 2, y or Y or (H - h) // 2, w, h, False
    )

def switch_to(window:Window):
    global screen

    if (scene := Window.current) is not None:
        scene.shown = False
        scene.canvas = scene.canvas.copy()
    Window.current = window

    if window is None:
        screen = _reset_video_system(size, flags | pg.HIDDEN)
        anchor[:] = None, None
        return size.clear()

    if window.size != size:
        size[:] = window.size
        screen = _reset_video_system(size, flags | pg.SHOWN, vsync=True)
    screen.blit(window.canvas, (0,0))
    pg.display.flip()
    window.canvas = screen
    window.shown = True

    return Action.scene_changed

def use(window:Window, relocation=True):
    if window is Window.current:
        return logger.warning(f"<{window = }> on scene")
    switch_to(window)

    if relocation:
        relocate()
        anchor[:] = window.anchor

    return Action.scene_changed

def hide(clear=True):
    if Window.current is None:
        return logger.error("window is already hidden")
    if clear:
        Window.current.queue.clear()
    use(None, False)

    return Action.break_loop

def parse_mouse_pos(pos):
    if pos is None:
        logger.error("mouse position is None")
    global hovering
    for widget in Window.current.logic_group:
        widget: pg.sprite.Sprite
        try:
            rect = widget.rect
        except AttributeError:
            continue

        if rect is None:
            logger.warning(f"{widget}.rect is None")
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
            return  # 假定同时只会hover一个

    if hovering is not None:
        hovering.situation = Situation.standby
        hovering = None

def parse_event(event):
    global pressed
    match event.type:
        case pg.MOUSEBUTTONDOWN:
            if event.button == pg.BUTTON_LEFT and hovering is not None:
                pressed = hovering
                pressed.situation = Situation.pressing
        case pg.MOUSEBUTTONUP:
            if event.button == pg.BUTTON_LEFT and pressed is not None:
                if pressed == hovering:
                    pressed.situation = Situation.clicked
                pressed = None
        case _:
            pass

def on_lose_focus():
    global hovering, pressed
    if hovering is not None:
        hovering.situation = Situation.standby
        hovering = None
    if pressed is not None:
        pressed.situation = Situation.standby
        pressed = None

def clear_each(window:Window):
    bgd = window.bgd
    blit = window.canvas.blit
    return [
        blit(bgd, rect:=widget.rect, rect)
        for widget in window.render_group
    ]

def clear_union(window:Window):
    it = iter(window.render_group)
    rect = next(it).rect.unionall([s.rect for s in it])
    return window.canvas.blit(window.bgd, rect, rect)

def clear_whole(window:Window):
    return window.canvas.blit(window.bgd, (0,0))

clear_strategy = Strategy.each

def on_clear(window:Window, heuristic=False):
    group = window.render_group
    if heuristic:
        global clear_strategy
        if len(group) > 12345:
            clear_strategy = Strategy.whole
            return clear_whole(window)
        else:
            if (total_size := sum(s.rect.font_size for s in group)) < \
               (union_size := (_:=clear_whole(window)).font_size()):
                logger.info(f"({total_size=}) < ({union_size=})")
                clear_strategy = Strategy.each
            else:
                logger.info(f"({total_size=}) > ({union_size=})")
                clear_strategy = Strategy.union
            return _
    else:
        match clear_strategy:
            case Strategy.each: return clear_each(window)
            case Strategy.union: return clear_union(window)
            case Strategy.whole: return clear_whole(window)
            case _: raise ValueError(type(clear_strategy), clear_strategy)

clock = pg.time.Clock()
target = 60
efficient = True
display_fps = True
title = "FPgui"
num = 0

def main_loop():
    if (scene := Window.current) is None:
        return logger.error("no window on scene")
    global num
    logic_group = scene.logic_group
    render_group = scene.render_group
    queue = scene.queue

    for num in count(num):
        # parse all events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return hide()
            else:
                parse_event(event)

        # parse mouse position
        if pg.mouse.get_focused():
            parse_mouse_pos(pg.mouse.get_pos())
        else:
            on_lose_focus()

        # evoke all callbacks from the queue
        while queue:
            """
            要先执行完queue再update
            因为有的update()可能会添加新的callback
            例如下一帧的动画什么的
            """
            callback, args, kwargs = queue.popleft()
            logger.info(f"calling {callback}(*{args}, **{kwargs})")
            if ans := callback(*args, **kwargs):
                if Action.scene_changed in ans:
                    logic_group = scene.logic_group
                    render_group = scene.render_group
                    queue = scene.queue

                ...

                if Action.break_loop in ans:
                    return hide()
 
        # update
        if logic_group:
            logic_group.update()
           
        # clear & render
        if render_group:
            on_clear(scene)
            pg.display.update(render_group.draw(screen))

        # tick
        _ = clock.tick(target) if efficient else clock.tick_busy_loop(target)
        if display_fps:
            pg.display.set_caption(f"{title} @ {1000/_ :.2f}")

def use_async(window:Window, relocation=True):
    threading.Thread(target=lambda: use(window, relocation) and main_loop()).start()
    return Action.scene_changed
