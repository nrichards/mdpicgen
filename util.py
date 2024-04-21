from pathlib import Path

from constants import GIF_IMAGE_EXTENSION, PNG_IMAGE_EXTENSION


def make_out_dir(out_dirname):
    Path(out_dirname).mkdir(parents=True, exist_ok=True)


def size_from_height(new_height, old_size) -> (int, int):
    old_width, old_height = tuple(old_size)

    reduction_scalar = new_height / old_height
    new_width = int(reduction_scalar * old_width)

    new_size = new_width, new_height
    return new_size


class ImageOpt:
    height: int
    gif: bool

    def __init__(self, height, gif):
        self.height = height
        self.gif = gif

    def extension(self):
        if self.gif:
            return GIF_IMAGE_EXTENSION
        else:
            return PNG_IMAGE_EXTENSION
