# FPgui —— 空前的GUI框架

![](others/logo.svg)

> 大量使用Python3.9的海象赋值符，少量使用Python3.10的match-case语法。体验该仓库时请注意解释器版本

## TODO / NotImplemented

- [x] 单元测试
- [ ] 实现HBox、VBox
- [ ] 实现anchor的分配
- [ ] 实现MinimizedButton

## 2022年3月23日大重构日志

- 完全脱离了`pygame`中的`Sprite`和`Group`的束缚
- 更符合逻辑的继承关系
- 渲染现在由`Container`完成，而不是由`ui`统一完成。因此`Window`类也不再维护`render_group`和`logic_group`两个变量
- `Being`类需要提供的接口也发生了更改，从原来的`image`和`rect`更改为现在的`surfs`列表，更加面向对象，且更加灵活
- 布局的**自上而下`layout`**机制和**自下而上`resize`**框架已建立

## Getting Start

- 以下展示python其他GUI框架（PyQt、WxPython等）所没有的特性
- 以下五行代码是一个简单而华丽的demo **（两三个大版本前的了，有空再改）**

```python
import time
from FPgui import ui
from label import Label, Monitor

with ui.using_async(ui.Window(1280, 720, 0)):
    Monitor(time.ctime, (80, 80), ui.Align.top_left, 18, (0, 255, 255), cache=False)
    Monitor("pg.mouse.get_pos()", (1200, 80), ui.Align.top_right, 18, (255, 0, 255))
    rand = Monitor("' '+f'{str(np.random.randint(0,10,5,np.uint8))[1:-1]} '*5", (640, 360), ui.Align.center, 22,
                   (0, 255, 0))
    Monitor(rand.raw_renderer.inspect, (640, 640), ui.Align.mid_bottom, 15, (255, 255, 255), cache=False)
```

- 上下文管理器`using_async`意味着事件循环运行在非主线程中(否则请使用`using`替代)，因此如果用 `ipython -i demo.py` 运行该脚本，你可以尝试在实时显示的同时更改界面
- 撕个“Label”展示Monitor类(一种特殊的Label)的“即时跟踪”特性
- 事实上，Monitor类的用途就是给运行会持续一段时间的程序一个除了命令行进度条之外的方法，或者用来实时显示中间变量以供debug

### 关于Monitor类传入的entity参数

1. 如果是`Callable`，那么追踪这个函数的返回值，demo中是time.ctime，其实也可以是一些获取当前某工作的进度的函数

2. 如果是`str`，由于静态的变量应该用`Label`类而非`Monitor`,所以`str`类型输入将被认为是要`eval()`的代码串，可以用来监控GUI内部的一些变量
    - 其实这也可以用来间接取值，比如某些变量（尤其是基本数据类型）值改变往往伴随着变量改变
    - 但其实这种情况用lambda表达式然后作为第1类传入更方便，应用场景其实不多（，或者可以用来减短代码？）

3. 否则，就用`repr`获取它的字符串。这种情况适用于监测一个列表或者字典。比如鼠标位置(正如上面代码展示的)

## 极致的 Pythonic

- `with` 用 **context manager** 配置界面
- `@decorator` 用装饰器语法添加回调函数(`button.py`中实现，未展示)

## 丰富的可扩展性

- 高度模块化。重要的函数和类，都封装完善
- 现有的类对继承友好，可复用性高

## 性能

- 失传的技术——精准的脏矩形渲染
- JIT加速的亚像素渲染和blend等图形操作
- 纳秒级的微优化，从细节做到极致

## 0学习成本

- hello world只需要最少2行（不含import语句），且可读性高
    - 如果不在乎可读性和单行长度的话，其实可以压缩到一行，并不是通过分号，但会用到很多海象赋值符

- 只需要numpy，pygame等常用的包，外加用来JIT编译黑魔法的numba库和用来高效缓存的blosc压缩库(或者blosc2但是目前blosc2不支持python3.10)

## 创建现代风的界面

- widgets.py提供了作者本人模仿一些UI/UX或者影视作品设计的组件预设，为大家提供灵感
    - 完成度不高，故暂时没有上传
