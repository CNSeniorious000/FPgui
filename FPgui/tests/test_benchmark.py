from FPgui import *
import os

os.system("del *.svg")  # pytest --benchmark-histogram


def test_get_size_valid(benchmark):
    widget = Widget(1, 2, 3, 4)
    benchmark(widget.get_size)


def test_get_size_null(benchmark):
    widget = Widget()
    benchmark(widget.get_size)


def test_get_anchor_valid(benchmark):
    widget = Widget(1, 2, 3, 4)
    benchmark(widget.get_anchor)


def test_get_anchor_null(benchmark):
    widget = Widget()
    benchmark(widget.get_anchor)
