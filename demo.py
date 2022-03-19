import time
from FPgui import ui, Align, scaling_at
from FPgui.label import Label, Monitor

# import FPgui as fp
# fp.DO_SCALE = False
# ui.efficient = False

with scaling_at(200), ui.Window((1280, 720), Align.bottom_right, (-4,-4), bgd=0).using() as window:
    Monitor(time.ctime, (80,80), ui.Align.top_left, 20, (0, 255, 255), cache=False)
    Monitor(lambda: f"FPS: {ui.clock.get_fps():.1f}", (1200, 80), ui.Align.top_right, 20, (255, 0, 255))
    rand = Monitor("' '+f'{str(np.random.randint(0,10,5,np.uint8))[1:-1]} '*5", (640,360), ui.Align.center, 24, (0, 255, 0))
    Monitor(rand.get_surface.inspect, (640, 80), ui.Align.mid_top, 16, (0, 255, 0), cache=False)
    Label("\n".join(i.strip() for i in """
    Hi! I'm a static label which never refresh.
    Labels around me called 'Monitors' showed its main usages:
    · The top-left one is the auto-refresh clock,
    · The top-right one is the fps display,
    · The center one is a always-updating random number generator,
    · And the mid-top one shows its caching information.
    Hope you enjoy the great performance and pythonic charm!
    """.strip().split("\n")) +"\n", (420, 672), ui.Align.bottom_left, 12, (255,) * 3)
    assert window.check(recursive=True)
