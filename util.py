from pathlib import Path


def make_out_dir(out_dirname):
    Path(out_dirname).mkdir(parents=True, exist_ok=True)


def size_from_height(new_height, old_size) -> (int, int):
    old_width, old_height = tuple(old_size)

    reduction_scalar = new_height / old_height
    new_width = int(reduction_scalar * old_width)

    new_size = new_width, new_height
    return new_size
