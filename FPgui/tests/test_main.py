from FPgui import ui, scaling_at, scaled

original_size = (444, 444)
ui.efficient = False


def test_gravity_demo():
    with scaling_at(25), ui.Window(original_size, bgd=(255,0,0)).using(90) as window:
        assert window.canvas.get_size() == tuple(scaled(original_size))
        assert scaled(4) == 1
        assert tuple(ui.size) == window.get_size() == window.size
        assert None not in ui.anchor

        class Mover(ui.Routine):
            def __init__(self):
                super().__init__()
                self.vx, self.vy = 44, 0
                assert window.check(recursive=True)

            def update(self):
                x, y = ui.anchor
                w, h = ui.DSIZE

                if not 0 <= x < w - window.w:
                    self.vx = -self.vx
                if not 0 <= y < h - window.h:
                    self.vy = -self.vy

                ui.move_window_to(x + self.vx, y + self.vy)
                assert ui.num_frames <= ui.max_frames

        mover = Mover()

        ui.add_task(lambda: exec("m.vy += 8", {}, {"m": mover}))

        assert mover.window is window
