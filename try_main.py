from base import *
import ui
from window import Window
from label import Monitor


win = Window(555, 666)

monitor = Monitor(win.render_group, ui.clock.get_fps, (222,333), subpixel=False)

ui.use(win)
ui.main_loop()
