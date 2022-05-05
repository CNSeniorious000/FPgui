from magic import *
from rich import *
import imageio

percentage = 0.03

while True:
    filepath = input(">>> ").strip('"')
    img = imageio.imread(filepath)
    y, x, _ = img.shape
    print(f"{img.shape = }")

    out = np.empty((y, x, 4), np.uint8)
    alpha = np.empty((y, x), np.uint8)
    alpha[:] = 255
    out[..., :3] = img[..., :3]

    radius = min(y, x) * percentage
    print(f"{radius = }")

    carver(alpha, radius)
    out[..., 3] = alpha

    output_path = f"{filepath[:filepath.rindex('.')]}_rounded.png"
    print(f"{output_path = }")

    imageio.imwrite(output_path, out)
    print("OK")
