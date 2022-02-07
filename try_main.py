import ui
from window import Window
from label import Monitor


a = [1,2,3,4]

def main():
    ui.flags = 0
    ui.use(win:=Window(1280, 720, 255))
    win.logic_group.add(monitor := Monitor(
        win.render_group, a, (640,360),
        subpixel=False, size=16, cache=False, align=ui.Align.bottom_right
    ))

if __name__ == '__main__':
    import threading
    main()
    ui.logger.info("after main")
    threading.Thread(target=ui.main_loop).start()
