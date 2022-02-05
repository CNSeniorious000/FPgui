import ui
from window import Window
from label import Monitor


win = Window(555, 666)

monitor = Monitor(win.render_group, ui.clock.get_fps, )

ui.use(win)
ui.main_loop()
