from black import main
import ui
from window import Window
from label import Monitor
import time

ui.use(win:=Window(1280, 720, 255))

a = [1,2,3,4]

win.logic_group.add(Monitor(
    win.render_group, a, (640,360),
    subpixel=False, size=12, cache=False, align=ui.Align.bottom_right
))

if __name__ == '__main__':
    import threading
    main = threading.Thread(target=ui.main_loop)
    main.start()