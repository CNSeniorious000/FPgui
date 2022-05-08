from FPgui import ui, scaling_at, scaled, Node

original_size = (444, 444)
ui.efficient = False


def test_gravity_demo():
    with scaling_at(25), ui.Window(original_size, align=ui.Align.top_left, bgd=(0, 0, 0)).using(84) as window:
        print(f"\n{ui.anchor = }")
        assert None not in ui.anchor  # still bug in there: this will fail if align is not ui.Align.top_left

        assert window.canvas.get_size() == tuple(scaled(original_size))
        assert scaled(4) == 1
        assert tuple(ui.size) == window.get_size() == window.size

        class Mover(Node):
            def __init__(self):
                super().__init__()
                self.vx, self.vy = 44, 0
                assert self in window.children

            def update(self):
                x, y = ui.anchor
                w, h = ui.DSIZE

                if not 0 <= x < w - window.w:
                    self.vx = -self.vx
                if not 0 <= y < h - window.h:
                    self.vy = -self.vy

                ui.move_to(x + self.vx, y + self.vy, ui.Align.top_left)
                assert ui.num_frames <= ui.max_frames

        mover = Mover()

        ui.routine(lambda: exec("m.vy += 8", {}, {"m": mover}))

        assert mover.root_window is window


def test_nested():  # FAILING: switching back is useless
    screenx, screeny = ui.DSIZE
    assert screenx // 16 == screeny // 9
    a = screenx // 16
    windows = ui.deque()
    with scaling_at(100):
        import time
        for i in range(16):
            for j in range(9):
                windows.append(context := ui.Window(
                    (a, a), (i * a, j * a), ui.Align.top_left, len(windows) + 111
                ).using(1))
                context.__enter__()
                time.sleep(0.01)
        for context in reversed(windows):
            context.__exit__(None, None, None)
