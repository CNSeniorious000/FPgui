from base import *
import pickle, bz2
from functools import cache, singledispatchmethod
import numpy as np
import numba as nb
import pygame as pg
from pygame import freetype; pg.init()
from PIL import Image, ImageDraw, ImageFont
from time import perf_counter as time

try:
    import blosc2 as blosc
    NOFILTER = blosc.Filter.NOFILTER
except ImportError:
    import blosc
    NOFILTER = blosc.NOSHUFFLE
finally:
    blosc.set_releasegil(True)

try:
    from cv2 import cv2
    def downscale(img:np.ndarray, size:tuple) -> np.ndarray:
        return cv2.resize(img, size, interpolation=cv2.INTER_AREA)
except ImportError:
    cv2 = NotImplemented
    @nb.njit(cache=True, parallel=True)
    def downscale(img:np.ndarray, size:tuple) -> np.ndarray:
        """a competitive implementation of INTER_AREA algorithm"""
        x, y = size
        c = img.ndim  # len(img.shape)
        if c == 3:
            h, w = img.shape[:2]
            out = np.empty((y, x, 3), np.uint8)
            xx, yy = w // x, h // y
            factor = xx * yy
            tmp = np.empty(3, dtype=np.float_)
            mm = 0
            for i in nb.prange(y):
                nn = 0
                for j in range(x):
                    tmp[0] = tmp[1] = tmp[2] = 0.5
                    for m in range(mm, mm + yy):
                        for n in range(nn, nn + xx):
                            tmp[0] += img[m, n, 0]
                            tmp[1] += img[m, n, 1]
                            tmp[2] += img[m, n, 2]
                    out[i, j, 0] = tmp[0] / factor
                    out[i, j, 1] = tmp[1] / factor
                    out[i, j, 2] = tmp[2] / factor

                    nn += xx
                mm += yy
        elif c == 2:
            h, w = img.shape
            out = np.empty((y, x), np.uint8)
            xx, yy = w // x, h // y
            factor = xx * yy
            mm = 0
            for i in nb.prange(y):
                nn = 0
                for j in range(x):
                    tmp = 0.5
                    for m in range(mm, mm + yy):
                        for n in range(nn, nn + xx):
                            tmp += img[m, n]
                    out[i, j] = tmp / factor

                    nn += xx
                mm += yy
        else:
            raise NotImplementedError
        return out


class memoize:
    instances = {}

    def __new__(cls, function):
        assert callable(function)
        try:
            return cls.instances[function.__name__]
        except KeyError:
            cls.instances[function.__name__] = _ = object.__new__(cls)
            _.__qualname__ = function.__qualname__
            _.__module__ = function.__module__
            _.__name__ = function.__name__
            _.__doc__ = function.__doc__
            return _

    def __init__(self, function):
        self._func = function
        self._data = {}
        self._info = {"count": [0, 0], "time": [0., 0.]}

    def __call__(self, *args):
        t = time()
        try:
            ans = self._data[args]
            self._info["count"][0] += 1
            self._info["time"][0] += time() - t
        except KeyError:
            ans = self._data[args] = self._func(*args)
            self._info["count"][1] += 1
            self._info["time"][1] += time() - t
        return ans

    def inspect(self):
        info = self._info
        return "" \
            f"hit -> {info['count'][0]} : {info['count'][1]} <- miss ||| " \
            f"hit -> {info['time'][0]:.0f} : {info['time'][1]:.0f} <- miss"

    @property
    def data(self):
        return self._data

    @property
    def info(self):
        return self._info

    @data.setter
    def data(self, data):
        self._data.update(data)

    @info.setter
    def info(self, info):
        self._info["count"][0] += info["count"][0]
        self._info["count"][1] += info["count"][1]
        self._info["time"][0] += info["time"][0]
        self._info["time"][1] += info["time"][1]

    @data.deleter
    def data(self):
        self.data.clear()

    @info.deleter
    def info(self):
        self._info = {"count": [0, 0], "time": [0., 0.]}

    @classmethod
    def save(cls, filename:str, *names):
        return bz2.open(f"./cache/{filename}.fpc", "wb").write(pickle.dumps(
            {name: (inst.data, inst.info) for name, inst in cls.instances.items() if name in names})
        ) if names else bz2.open(f"./cache/{filename}.fpc", "wb").write(pickle.dumps(
            {name: (instance.data, instance.info) for name, instance in cls.instances.items()})
        )

    @classmethod
    def load(cls, filename:str, *names):
        _ = pickle.loads(bz2.open(f"./cache/{filename}.fpc").read())
        for name in names if names else cls.instances.keys():
            cls.instances[name].data = _[name][0]
            cls.instances[name].info = _[name][1]


class memoize_surfaces(memoize):
    pass







    @singledispatchmethod
    def blit(self, *_, **__):
        return NotImplemented


if "debug":
    def show(arr):
        from matplotlib import pyplot as plt
        plt.imshow(arr)
        plt.show()

    def show_cv2(arr, name=None):
        from cv2 import cv2
        cv2.imshow(f"{arr.shape = }" if name is None else name, arr)
        cv2.waitKey(1)

    def show_surface(surface:pg.Surface):
        show(pg.surfarray.pixels3d(surface).swapaxes(0,1))

    def show_surface_alpha_cv2(surface):
        show_cv2(pg.surfarray.array_alpha(surface).T, f"{surface}")

    def print_and_return(*args):
        from rich import inspect
        for arg in args:
            inspect(arg)
        return args

    def test_carver(r):
        a = np.empty((100, 100), np.uint8)
        a[:] = 255
        try:
            carver(a, r)
        except IndexError as e:
            print(e)
        finally:
            show(a)
        return a


@nb.njit(cache=True)
def dist(i, j, r):
    return ( i*i + j*j + 2*(r-i-j)*r ) ** 0.5

@nb.njit(cache=True, parallel=True)
def tailor(alpha:np.ndarray, radius:float):
    r = int(radius) + 1
    for i in nb.prange(r):
        for j in range(r-i):
            weight = max(0.0,min(  1+radius-dist(i,j,radius)  ,1.0))
            alpha[i,j] *= weight
            alpha[-1-i,j] *= weight
            alpha[i,-1-j] *= weight
            alpha[-1-i,-1-j] *= weight

@nb.njit(cache=True, parallel=True)
def carver(alpha:np.ndarray, radius:float):
    r = int(radius) + 1
    for i in nb.prange(r):
        for j in range(r):
            alpha[i,j] = alpha[-1-i,j] = alpha[i,-1-j] = alpha[-1-i,-1-j] = 0

    mid = int(min(alpha.shape) / 2 - radius)
    end = 1 + int(radius * np.log(128 * radius))
    if mid < end:
        print("WARNING: mid = " + str(mid), "while end = " + str(end))

    loss = radius % 1
    # for _i in nb.prange(end):
    for _i in nb.prange(min(mid, end)):
        fx = int((radius * np.e ** ((loss-_i) / radius)) * 256 - 1)
        i = _i + r
        y = fx // 256
        alpha[i,y] = alpha[-1-i,y] = alpha[i,-1-y] = alpha[-1-i,-1-y] = \
        alpha[y,i] = alpha[-1-y,i] = alpha[y,-1-i] = alpha[-1-y,-1-i] = 255 - fx % 256
        for j in range(y):
            alpha[i,j] = alpha[-1-i,j] = alpha[i,-1-j] = alpha[-1-i,-1-j] = \
            alpha[j,i] = alpha[-1-j,i] = alpha[j,-1-i] = alpha[-1-j,-1-i] = 0

def filter_robust(alpha:np.ndarray, color:np.ndarray, direction=0):
    match direction, color.ndim:
        case _, 3: assert color.shape[:2] == alpha.shape
        case 0, 1: return filter_monochrome(alpha, color)
        case 0, 2: return filter_chromatic(alpha, color)
        case 90, 1: ...
        case 90, 2: ...
        case 180, 1: ...
        case 180, 2: ...
        case 270, 1: ...
        case 270, 2: ...

@nb.njit(cache=True, parallel=True)
def filter_monochrome(raw:np.ndarray, c_arr:np.ndarray):
    pass

@nb.njit(cache=True, parallel=True)
def filter_chromatic(raw:np.ndarray, y:int, x:int, c_arr:np.ndarray):
    filtered_img = np.empty((y,x))
    for i in nb.prange(y):
        filtered_img[i] = kernel_spread(raw[i], c_arr)[..., 2:-2]
    return filtered_img

@nb.stencil
def kernel_spread(raw:np.ndarray, c_arr:np.ndarray):
    return raw[-2] * c_arr[-2] * c_arr[-1] + \
           raw[-1] * c_arr[-1] * (c_arr[-1]+c_arr[0]) + \
           raw[0] * c_arr[0] * (c_arr[-1]+c_arr[0]+c_arr[1]) + \
           raw[1] * c_arr[1] * (c_arr[1] +c_arr[0]) + \
           raw[2] * c_arr[2] * c_arr[1]

@nb.njit(cache=True, parallel=True)
def remix(alpha:np.ndarray, color:np.ndarray, canvas:np.ndarray, bbox:tuple):
    """blending on canvas with subpixel alpha and unique color"""
    x, y, w, h = bbox
    r, g, b = color
    for i in nb.prange(h):
        for j in range(w):
            canvas[y+i, x+j, 0] = canvas[y+i, x+j, 0] * (1 - alpha[i, j, 0]) + r * alpha[i, j, 0]
            canvas[y+i, x+j, 1] = canvas[y+i, x+j, 1] * (1 - alpha[i, j, 1]) + g * alpha[i, j, 1]
            canvas[y+i, x+j, 2] = canvas[y+i, x+j, 2] * (1 - alpha[i, j, 2]) + b * alpha[i, j, 2]

def paintln(text, color, font_path, font_size, align="left", subpixel=False):
    """TODO: implement this"""
    return paint_PIL(text, color, font_path, font_size, align)

@memoize_surfaces
def paint_PIL(text:str, color, font_path, font_size, align="left"):
    ImageDraw.Draw(canvas := Image.new(
        "RGBA", size := (font := get_PIL_font(font_path, font_size)).getsize_multiline(text)
    )).multiline_text((0,0), text, color, font, align=align)
    return pg.image.frombuffer(np.asarray(canvas), size, "RGBA").convert_alpha()

@memoize_surfaces
def paint_PIL_subpixel(text:str, color, font_path, font_size, align="left"):
    width, height = (font := get_PIL_font(font_path, font_size*3)).getsize_multiline(text)
    if align == "left":
        xy = (0, 0)
    else:
        loss = width % 3
        xy = (loss, 0) if align == "right" else (loss // 2, 0)

    w, h = (width + 2) // 3, (height + 2) // 3

    ImageDraw.Draw(canvas := Image.new("L", (w,h))).multiline_text(xy, text, 255, font, align=align)

    return pg.image.frombuffer(
        filter_chromatic(np.asarray(canvas), h, w, np.array(color) / 255), (w, h), "RGBA").convert_alpha()

@cache
def paintln_FP(text:str, font:str, size:int, canvas_size:tuple, t_c:np.ndarray):
    PILfont = ImageFont.truetype(font, SS3x*size*3)
    w, h = canvas_size
    canvas = Image.new("L", [SS3x*(w*3+4), SS3x*h*3], 0)
    ImageDraw.Draw(canvas).text([SS3x*2,0], text, 255, PILfont)
    return (
        filter_chromatic(
            downscale(
                np.asarray(
                    canvas, dtype=np.float_
                ), (w*3+4, h)
            )/255, h, w*3, np.tile(t_c/sum(t_c), w+2)[1:-1]
        ).reshape((h, w, 3))
    ).swapaxes(0,1)

@cache
def get_PIL_font(path, size):
    return ImageFont.truetype(path, round(size))

@cache
def get_PG_font(path, size):
    font = freetype.Font(path, size)
    font.kerning = True
    font.pad = True
    return font

def get_window_using():
    import ui
    return ui.scene
