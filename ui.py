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
        screen.blit(window.canvas, (0,0))
    window.canvas = screen
    window.shown = True

    return Action.scene_changed

def center():
    hWnd = pg.display.get_wm_info()["window"]
    X, Y = display_size
    x, y = size
    ctypes.windll.user32.MoveWindow(hWnd, (X-x)//2, (Y-y)//2, x, y, False)

def use(window:Window, centering=True):
    if window is scene:
        return logger.warning(f"<{window = }> on scene")
    switch_to(window)

    if centering:
        center()

    pg.display.flip()

    return Action.scene_changed

def hide(clear=True):
    if scene is None:
        return logger.error("window is already hidden")
    if clear:
        scene.queue.clear()
    use(None, False)

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
            return  # 假定同时只会hover一个
    else:
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
            if (total_size := sum(s.rect.size for s in group)) < \
               (union_size := (_:=clear_whole(window)).size()):
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

target = 60
efficient = True
display_fps = True
title = "FPgui"

def main_loop():
    if scene is None:
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

        # render
        if render_group:
            on_clear(scene)
            pg.display.update(render_group.draw(screen))

        # tick
        _ = clock.tick(target) if efficient else clock.tick_busy_loop(target)
        if display_fps:
            pg.display.set_caption(f"{title} @ {1000/_ :.2f}")
