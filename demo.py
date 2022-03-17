import ui, time
from label import Label, Monitor


ui.using_async(ui.Window(1280, 720, 0))
Monitor(time.ctime, (80,80), ui.Align.top_left, 18, (0,255,255), cache=False)
Monitor(lambda: f"FPS: {ui.clock.get_fps():.1f}", (1200, 80), ui.Align.top_right, 18, (255,0,255))
rand = Monitor("' '+f'{str(np.random.randint(0,10,5,np.uint8))[1:-1]} '*5", (640,360), ui.Align.center, 22, (0,255,0))
Monitor(rand.get_surface.inspect, (640, 80), ui.Align.mid_top, 15, (0,255,0), cache=False)

Label("\n".join(i.strip() for i in """
Hi! I'm a static label which never refresh.
Labels around me called 'Monitors' showed its main usages:
· The top-left one is the auto-refresh clock,
· The top-right one is the fps display,
· The center one is a always-updating random number generator,
· And the mid-top one shows its caching infomation.
Hope you enjoy the great performance and pythonic charm!
""".strip().split("\n"))+"\n", (420, 670), ui.Align.bottom_left, 12, (255,)*3)