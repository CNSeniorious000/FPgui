import ui
from window import Window
from label import Monitor


win = Window(555, 666)
ui.use(win)
ui.main_loop()
