import ui
from window import Window
from label import Monitor

a = [1,2,3,4]

win = Window(1280, 720, 255)
# ui.use(win)

def main():
    ui.use(win)
    win.logic_group.add(monitor := Monitor(
        win.render_group, a, (640,360),
        subpixel=False, size=18, cache=False, align=ui.Align.center
    ))
    ui.main_loop()

if __name__ == '__main__':
    import threading
    ui.hide()

    # main()

    thread = threading.Thread(target=main)
    thread.start()
    thread.join()
