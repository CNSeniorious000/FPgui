from base import *
import ui
from window import Window
from label import Monitor
from random import randint


win = Window(1280, 720, 255)

win.logic_group.add(monitor:=Monitor(
    win.render_group, ui.clock.get_fps, (640,360), subpixel=False, size=50)
)

ui.use(win)
ui.main_loop()
