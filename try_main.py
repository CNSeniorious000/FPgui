import ui
from window import Window
from label import Monitor
import time
import threading

a = [1,2,3,4]

win = Window(1280, 720, 255)
win.logic_group.add(monitor := Monitor(
    win.render_group, lambda: ui._reset_video_system, (640,360),
    subpixel=False, size=18, cache=False, align=ui.Align.center
))

def main():
    ui.use(win)
    ui.main_loop()

def side_main():
    thread = threading.Thread(target=main)
    thread.start()
    return thread


if __name__ == '__main__':
    main()
    side_main().join()
    side_main().join()
    side_main().join()
    main()
    main()
    side_main()
