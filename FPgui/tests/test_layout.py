from FPgui import *
from FPgui import ui
from FPgui.layout import Window


def test_align_name():
    assert Align.min_x is Align.left
    assert Align.max_x is Align.right
    assert Align.min_y is Align.top
    assert Align.max_y is Align.bottom


def test_align_in():
    assert Align.min_x in Align.top_left
    assert Align.min_x in Align.mid_left
    assert Align.min_x in Align.bottom_left
    assert Align.mid_x in Align.mid_top
    assert Align.mid_x in Align.center
    assert Align.mid_x in Align.mid_bottom
    assert Align.max_x in Align.top_right
    assert Align.max_x in Align.mid_right
    assert Align.max_x in Align.bottom_right


def test_align_combinations():
    assert Align.min_y & Align.top_left is Align.min_y & Align.top_right is Align.min_y
    assert Align.mid_y & Align.mid_left is Align.mid_y & Align.mid_right is Align.mid_y
    assert Align.max_y & Align.bottom_left is Align.max_y & Align.bottom_right is Align.max_y

    assert not Align.left & Align.right
    assert not Align.top & Align.bottom

    assert Align.left | Align.right not in Align
    assert Align.top | Align.bottom not in Align

    for h in Align.min_x, Align.mid_x, Align.max_x:
        for v in Align.min_y, Align.mid_y, Align.max_y:
            assert h | v in Align

    assert not any(Align.bottom_right.translate_to_top_left(123, 234, 123, 234))


def test_MinimizedWidget():
    widget = Rect(1, 2, 3, 4, Align.center)
    assert widget.align == Align.center
    assert widget.w, widget.h == widget.size == widget.get_size()
    assert widget.x, widget.y == widget.anchor == widget.get_anchor()
    assert widget.align_v == "center"

    del widget.size
    assert widget.w is widget.h is None

    widget.del_anchor()
    assert widget.x is widget.y is None

    widget.set_size([100, 200])
    assert widget.w, widget.h == [100, 200]

    widget.anchor = [300, 400]
    assert widget.x, widget.y == [300, 400]


def test_Widget():
    with Window((0, 0)):
        widget = Widget()
        assert widget.get_size() == widget.size
        assert widget.get_anchor() == widget.anchor

        assert widget.fixed is False
        widget.size = [1, 2]
        assert widget.fixed is True
        del widget.size
        assert widget.fixed is False


def test_Being():
    with Window((1234, 2345)):
        widget = Being()
        assert widget.dirty is False
        widget.dirty = True
        assert widget.dirty is True


def test_Node():
    assert Window.current is ui.current_parent is None

    with scaling_at(100), Window(DSIZE, bgd=(255, 0, 0)).using(1) as window:
        assert Window.current is not None
        node = Node()
        assert node.root is window is Window.current


def test_Window():
    with scaling_at(100):
        with Window(DSIZE, bgd=(0, 255, 0)).using(1) as window_green:
            assert Window.current is ui.current_parent is window_green
            assert list(window_green.size) == DSIZE

            with Window(DSIZE, bgd=(0, 0, 255)).using(1) as window_blue:
                assert Window.current is ui.current_parent is window_blue
                assert window_blue.window is window_blue.root is window_green, "但没关系"


def test_ui():
    assert ui._reset_video_system.__name__ == ui.pg.display.set_mode.__name__
