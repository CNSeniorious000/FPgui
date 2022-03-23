import time
from FPgui import ui, Align, scaling_at, Node
from FPgui.label import StaticText, Monitor


with scaling_at(125), ui.Window((1280, 720), (-40,-40), Align.bottom_right, bgd=0).using(200) as window:
    Monitor(time.ctime, (80,80), Align.top_left, 20, (0, 255, 255), cache=False)
    Monitor(lambda: f"{100 * ui.num_frames / ui.max_frames :.0f}%", (1200, 80), Align.top_right, 20, (255, 0, 255))
    rand = Monitor("' '+f'{str(np.random.randint(0,10,5,\"i8\"))[1:-1]} '*5", (640,360), Align.center, 24, (0, 255, 0))
    Monitor(rand.get_surface.inspect, (640, 80), Align.mid_top, 16, (0, 255, 0), cache=False)
    StaticText("\n".join(i.strip() for i in """
    Hi! I'm a static label which never refresh.
    Labels around me called 'Monitors' showed its main usages:
    · The top-left one is the auto-refresh clock,
    · The top-right one is the fps display,
    · The center one is a always-updating random number generator,
    · And the mid-top one shows its caching information.
    Hope you enjoy the great performance and pythonic charm!
    """.strip().split("\n")) +"\n", (420, 672), Align.bottom_left, 12, (255,) * 3)

    class Mover(Node):
        def __init__(self):
            super().__init__(window)
            self.vx = self.vy = 1

        def update(self):
            x, y = ui.anchor
            w, h = ui.DSIZE

            if not 0 <= x < w - window.w:
                self.vx = -self.vx
            if not 0 <= y < h - window.h:
                self.vy = -self.vy

            # ui.move_to(x + self.vx, y + self.vy, Align.top_left)
            ui.move(self.vx, self.vy)

    # ui.routine(lambda: ui.pg.image.save(window.canvas, f"./FPgui/cache/{ui.num_frames=}.png"))

    Mover()
