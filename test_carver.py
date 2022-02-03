from magic import *
from alive_progress import alive_it

size = 750
arr1 = np.empty((size*2, size*2), np.uint8)
arr2 = np.empty((size * 4, size * 4), np.uint8)


@memoize
def show_icon(r):
    arr1[:] = 255
    arr2[:] = 0
    carver(arr1, r)
    arr2[size:size*3, size:size*3] = arr1
    return downscale(arr2, arr1.shape)


if __name__ == '__main__':
    import math

    scale_x = 25
    scale_y = 50

    left = int(np.pi * scale_x / 2)
    right = left * 3

    try:
        # n = 0
        while True:
            for i in alive_it(range(left, right)):
                show_cv2(show_icon(scale_y*1.3 + math.sin(i/scale_x) * scale_y))
                # cv2.imwrite(f"./{n}.png", show_icon(scale_y*1.5 + math.sin(i/scale_x) * scale_y))
                # n += 1

            for i in alive_it(range(right, left, -1)):
                show_cv2(show_icon(scale_y*1.3 + math.sin(i/scale_x) * scale_y))
                # cv2.imwrite(f"./{n}.png", show_icon(scale_y*1.5 + math.sin(i/scale_x) * scale_y))
                # n += 1
            # break

    except KeyboardInterrupt:
        print(show_icon.inspect())
