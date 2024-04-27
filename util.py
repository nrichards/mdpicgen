from pathlib import Path

from constants import GIF_IMAGE_EXTENSION, PNG_IMAGE_EXTENSION, SHORT_NAME_INFIX_SEPARATOR


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


def format_image_basename(button_sequence) -> str:
    """
    Creates a basename suitable for representing a button sequence.
    
    Example:
        Input: [{'MODE PLAY (RECALL)': 'mplay'}, {'B[1-8]': '12345678'}, {'turn dial': 'dial'}]
        Output: 'mplay_12345678_d'

    Uses separator character (_) between buttons, 
    except for commands with multiple-choice numbered buttons.
    """
    return SHORT_NAME_INFIX_SEPARATOR.join([list(command.values())[0] for command in button_sequence])
