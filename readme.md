# FPgui —— 空前的GUI框架

## hello world

- 五行展示Monitor的“即时跟踪”特性
- 整个GUI运行在非主线程中，因此推荐用`ipython -i demo.py`运行，你可以尝试在运行时查看各种中间变量，体会整个框架的精妙

```python
import ui, time
from label import Label, Monitor

with ui.make_async_window(1280, 720, 0) as window:
    Monitor(time.ctime, (80,80), ui.Align.top_left, 18, (0,255,255), cache=False)
    Monitor(lambda: f"FPS: {ui.clock.get_fps():.1f}", (1200, 80), ui.Align.top_right, 18, (255,0,255))
    rand = Monitor("' '+f'{str(np.random.randint(0,10,5,np.uint8))[1:-1]} '*5", (640,360), ui.Align.center, 22, (0,255,0))
    Monitor(rand.get_surface.inspect, (640, 640), ui.Align.mid_bottom, 15, (255,255,255), cache=False)
```

## 极致的 Pythonic

- `with context manager` 用上下文管理器配置界面

- `@decorator` 用装饰器语法添加回调函数

## 丰富的可扩展性

- 高度模块化
- 可复用度高

## 注重性能

- 失传的技术——精准的藏举行渲染
- 纳秒级的微优化，从细节做到极致
- JIT加速的亚像素渲染和blend等图形操作

## 0学习成本

- hello world只需要最少2行（不含import语句），且可读性高

## 现代界面

- 堪比WEB的自由度，辅以高效的渲染
