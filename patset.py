import csv
import io
import re
from pathlib import Path

from constants import PATTERN_FILE_DELIMITER, SEPARATOR_VALUE_WRAPPER, COMMENT_KEY, SEPARATOR_KEY, TABLE_HEADER_KEY


def load_values_from_csv(button_pattern_file, find_key, delimiter=PATTERN_FILE_DELIMITER):
    result = [
        row[1].strip().strip(SEPARATOR_VALUE_WRAPPER)
        for row in csv.reader(io.StringIO(button_pattern_file), delimiter=delimiter)
        if row and row[0].startswith(find_key)
    ]

    return result


def load_constants_from_csv(button_pattern_file: str, delimiter=PATTERN_FILE_DELIMITER) -> \
        {re.Pattern, str}:
    """
    Return a dict of regular expressions and their equivalent string identifiers.

    To be used to match button names to short-form, well-known button identifiers.
    """
    constants = {}
    for row in csv.reader(io.StringIO(button_pattern_file), delimiter=delimiter):
        if not row or row[0].startswith((COMMENT_KEY, SEPARATOR_KEY, TABLE_HEADER_KEY)):
            continue

        key, value = row
        ks = key.strip()
        kre = re.compile(ks, re.IGNORECASE)
        constants[kre] = value.strip()
    return constants


def patterns_to_header(button_pattern_file):
    button_pattern_data = Path(button_pattern_file).read_text()
    values = load_values_from_csv(button_pattern_data, TABLE_HEADER_KEY)
    result = values[0].strip()
    return result


def patterns_to_separators(button_pattern_file) -> [str]:
    button_pattern_data = Path(button_pattern_file).read_text()
    return load_values_from_csv(button_pattern_data, SEPARATOR_KEY)


def patterns_map_to_button_name(button_pattern_file) -> {str, str}:
    """
    String patterns of button control found in a document,
    and their canonical names.
    Patterns use regular expressions.
    Case-insensitive, specially handled elsewhere by code.
    Equals (=) separates the word and its value. See BUTTON_PATTERN_DELIMITER.
    """
    pattern_to_canonical_button_name = Path(button_pattern_file).read_text()

    return load_constants_from_csv(pattern_to_canonical_button_name)
