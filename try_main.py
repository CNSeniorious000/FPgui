import ui
from window import Window
from label import Monitor


a = [1,2,3,4]

def main():
    ui.flags = 0
    ui.use(win:=Window(1280, 720, 255))
    win.logic_group.add(monitor := Monitor(
        win.render_group, a, (640,360),
        subpixel=False, size=16, cache=False, align=ui.Align.center
    ))
    ui.main_loop()

if __name__ == '__main__':
    import threading

    # main()

    thread = threading.Thread(target=main)
    thread.start()
    thread.join()
