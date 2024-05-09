from pathlib import Path
from typing import Iterable

from mistletoe.token import Token

from constants import GIF_IMAGE_EXTENSION, PNG_IMAGE_EXTENSION, SHORT_NAME_INFIX_SEPARATOR


def make_out_dir(out_dirname):
    """ XOX ! """
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


def extract_digit_ranges(text):
    """Extract positively incrementing ranges separated by hyphens, and other digits.
    
    Example: [1-3, 7,8] => 12378
    
    See: test_extract_md.py
    """
    extracted = []
    start_digit = None
    last_digit = None
    # E.g. "[1-3, 7,8]"
    for char in text:
        # If this is a digit: "1-3, 7,8]" or "3, 7,8]" or "7,8]" or 8]"
        if char.isdigit():
            digit = int(char)
            # If we are in a range: "3, 7,8]"
            if start_digit is not None:
                end_digit = digit
                # Add digit to result, including preceding digits in range, excepting the start digit
                extracted.extend(range(start_digit + 1, end_digit + 1))
                # No longer in a range
                start_digit = None
            else:
                # Add digit to result: "1-3, 7,8]" or "7,8]" or 8]"
                extracted.append(digit)
            last_digit = digit
        # If we are starting a range: "-3, 7,8]"
        elif char == '-' and last_digit is not None:
            start_digit = last_digit
        # If we are breaking a range
        else:
            start_digit = None
    # Convert to string
    result = "".join([str(x) for x in extracted])
    return result


def strip_whitespace(sequence):
    return list(map(str.strip, sequence))


def find_first_non_null_index(a_list):
    return next((i for i, x in enumerate(a_list) if x is not None), -1)


def print_markdown_tree(mistletoe_children: [Token], level=0):
    """
    print a formatted tree to stdout of mistletoe Tokens
    :param mistletoe_children: list of mistletoe Tokens
    :param level: 
    :return: 
    """

    def print_helper():
        current = padding * level + str(child)
        print(current)

    padding = "|   "
    children = mistletoe_children

    if not is_iterable(children):
        print_helper()
        return

    for child in children:
        print_helper()

        if hasattr(child, 'children') and child.children:
            print_markdown_tree(child.children, level + 1)


def is_iterable(obj):
    return isinstance(obj, Iterable)


def find_nearest_less_than_or_equal(list_of_tuples: [(int, str)], search_value):
    """Finds the nearest less-than-or-equal number from a list of tuples.
  
    Args:
        list_of_tuples: A list of tuples where the first element is an integer.
        search_value: The integer to search for.
  
    Returns:
        A tuple containing the nearest less-than-or-equal number and its corresponding data,
         or None if no such number exists.
    """
    closest_value = None
    closest_data = None

    for num, _ in list_of_tuples:
        if num <= search_value:
            # Update if closer or the first match
            if closest_value is None or num >= closest_value:
                closest_value = num
                closest_data = _

    return closest_value, closest_data


def truncate(text, elide_length=15):
    return (text[:elide_length] + "...") if elide_length < len(text) else text


def find_category_names(sentence: str, categories: [{str: [str]}]) -> [str]:
    """Finds category names for keywords found in the sentence.
    
    Args:
        sentence: A string containing the input sentence.
        categories: An ordered list of dictionaries mapping category names to lists of keywords.
    
    Returns:
        A list of category names for which keywords are found in the sentence.
    """
    found_names = []
    # Convert sentence to lowercase for case-insensitive matching
    lowercase_sentence = sentence.lower()

    for category in categories:
        for name, keywords in category.items():
            # Check if any keyword is found in the sentence (ignoring case)
            if any(keyword in lowercase_sentence for keyword in keywords):
                found_names.append(name)

    return found_names
