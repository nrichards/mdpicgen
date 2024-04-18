import csv
import io
import os
import re
import sys
from collections import Counter
from pathlib import Path

from mistletoe.block_token import Table, TableRow, Document
from mistletoe.markdown_renderer import MarkdownRenderer
from mistletoe.span_token import RawText, HtmlSpan

from constants import HTML_BREAK_PATTERN

# For debugging parsing
DEBUG_LOG_EXTRACT = False

# For generating image filenames, the separator between alphanumeric chars, e.g. "s_mplay_123"
SHORT_NAME_INFIX_SEPARATOR = "_"

# For reading the pattern text file
PATTERN_FILE_DELIMETER = "="
TABLE_HEADER_KEY = "__header__"
SEPARATOR_KEY = "__separator__"
SEPARATOR_VALUE_WRAPPER = "\""  # just a quote, for later stripping of the quoted string values
COMMENT_KEY = "#"


def extract_button_sequences(md_file, but_pat_file) -> [[]]:
    """
    Extract button command sequences from Markdown following a set of patterns

    :param md_file: Markdown file formatted with well-known button sequences in special tables
    :param but_pat_file: Text file mapping regular expressions to buttons, and defining separator patterns
    :return: List of dictionaries mapping recognized button names, as written in the input Markdown, to short names
    which are used as components of basenames of generated image files illustrating the button sequence
    """
    extractor = ExtractButtonsFromMarkdown(md_file, but_pat_file)
    if DEBUG_LOG_EXTRACT:
        print(f"rejected: {len(extractor.could_not_find)}", file=sys.stderr)
    return extractor.button_sequences


def format_image_basename(button_sequence) -> str:
    """
    Creates a basename suitable for representing a button sequence.

    Example:
        Input: [{'MODE PLAY (RECALL)': 'mplay'}, {'B[1-8]': '12345678'}, {'turn dial': 'dial'}]
        Output: 'mplay_12345678_d'

    Uses separator character (_) between buttons, excepting the numbered buttons.
    Numbered buttons will be run together without separator characters.
    """
    result = ""
    last_is_digit = False
    for bmap in button_sequence:
        _, value = list(bmap.items())[0]

        curr_isdigit = value.isdigit()

        # Insert a separator character between prior and current button short-names
        # unless both names are digits.
        if len(result) and not (last_is_digit and curr_isdigit):
            result = result + SHORT_NAME_INFIX_SEPARATOR

        result = result + value

        last_is_digit = curr_isdigit
    return result


class ButtonSequence:
    sequence_mapping: [{}]
    line_number: int
    basename: str = ""

    def __init__(self, mapping, line_no):
        self.sequence_mapping = mapping
        self.line_number = line_no
        self.basename = format_image_basename(self.sequence_mapping)

    @staticmethod
    def to_sequence_mapping_list(button_sequences: ["ButtonSequence"]):
        """
        Extracts a list of button sequence strings, mapping to shortnames, from an input list of ButtonSequences
        """
        if button_sequences and type(button_sequences[0]) is not ButtonSequence:
            print(
                f"error: can't transform extracted mapping to sequence list, unsupported type: {type(button_sequences[0])}")
            return

        result = [seq.sequence_mapping for seq in button_sequences]

        return result


class ExtractButtonsFromMarkdown:
    """
    Extracts button command sequences from tables in Markdown.
    """
    # Output
    buttons: [[]] = []  # [{'SHIFT': 's'}, {'SEQ PLAY': 'splay'}, {'turn dial': 'd'}] -- for example
    button_sequences: [ButtonSequence] = []  # Also contains line numbers
    could_not_find = []  # Sequences not matched by the patterns

    # Options
    require_br_tag = True  # "SHIFT + SEQ PLAY + turn dial <br> ..." -- default constraint

    def __init__(self, markdown_filename, button_pattern_file):
        self.button_patterns = self.patterns_map_to_button_name(button_pattern_file)
        self.separators = self.patterns_to_separators(button_pattern_file)
        self.header = self.patterns_to_header(button_pattern_file)

        with open(markdown_filename, "r") as fin:
            with MarkdownRenderer(normalize_whitespace=True) as renderer:
                document = Document(fin)

                # Extract buttons, following constraints and patterns, and store results
                result = self.extract_document(document)
                self.button_sequences = result
                self.buttons = ButtonSequence.to_sequence_mapping_list(self.button_sequences)

    def patterns_map_to_button_name(self, button_pattern_file) -> {str, str}:
        """
        String patterns of button control found in a document,
        and their canonical names.
        Patterns use regular expressions.
        Case-insensitive, specially handled elsewhere by code.
        Equals (=) separates the word and its value. See BUTTON_PATTERN_DELIMITER.
        """
        pattern_to_canonical_button_name = Path(button_pattern_file).read_text()

        return self.load_constants_from_csv(pattern_to_canonical_button_name)

    def patterns_to_separators(self, button_pattern_file):
        button_pattern_data = Path(button_pattern_file).read_text()
        return self.load_values_from_csv(button_pattern_data, SEPARATOR_KEY)

    def patterns_to_header(self, button_pattern_file):
        button_pattern_data = Path(button_pattern_file).read_text()
        values = self.load_values_from_csv(button_pattern_data, TABLE_HEADER_KEY)
        result = values[0].strip()
        return result

    def load_constants_from_csv(self, button_pattern_file: str, delimiter=PATTERN_FILE_DELIMETER) -> \
            {re.Pattern, str}:
        """
        Return a dict of regular expressions and their equivalent string identifiers.

        To be used to match button names to short-form, well-known button identifiers.
        """
        constants = {}
        for row in csv.reader(io.StringIO(button_pattern_file), delimiter=delimiter):
            if not row:
                continue
            if (row[0].startswith(COMMENT_KEY) or row[0].startswith(SEPARATOR_KEY) or
                    row[0].startswith(TABLE_HEADER_KEY)):
                continue

            key, value = row
            ks = key.strip()
            kre = re.compile(ks, re.IGNORECASE)
            constants[kre] = value.strip()
        return constants

    def load_values_from_csv(self, button_pattern_file, find_key, delimiter=PATTERN_FILE_DELIMETER):
        result = []
        for row in csv.reader(io.StringIO(button_pattern_file), delimiter=delimiter):
            if row and row[0].startswith(find_key):
                _, value = row
                result = result + [value.strip().strip(SEPARATOR_VALUE_WRAPPER)]
        return result

    def extract_document(self, doc) -> [ButtonSequence]:
        result = []
        for token in doc.children:
            if type(token) is Table:
                result = result + self.extract_table(token)
        return result

    def extract_table(self, table: Table) -> [ButtonSequence]:
        result = []
        if self.is_button_table(table):
            for element in table.children:
                extract = self.extract_tablerow(element)

                # wrap subarray
                if extract:
                    result = result + [extract]
        return result

    def is_button_table(self, table) -> bool:
        label = table.header.children[0].children[0]
        if type(label) is RawText:
            if label.content.lower().startswith(self.header.lower()):
                return True
        return False

    def extract_tablerow(self, tablerow: TableRow) -> ButtonSequence:
        result = []
        button_sequence = []

        # first cell: assumes first column of table
        cell = tablerow.children[0]

        # constrain to require <br> tag
        if self.require_br_tag:
            has_enough_children = len(cell.children) > 1
            is_first_token_raw_text = len(cell.children) > 0 and type(cell.children[0]) is RawText
            has_html_br_tag_as_second_token = \
                (has_enough_children and
                 type(cell.children[1]) is HtmlSpan and
                 re.match(HTML_BREAK_PATTERN, cell.children[1].content, re.IGNORECASE))

            if has_enough_children and is_first_token_raw_text and has_html_br_tag_as_second_token:
                # Extract the first token with content.
                # Presumes "B1 <br> ![](path-to-image)", and extracts "B1". Also supports no image.
                token = cell.children[0]
                button_sequence = self.extract_rawtext(token)
            else:
                if DEBUG_LOG_EXTRACT:
                    print(f"ignored cell{', needs more children' if not has_enough_children else ''}"
                          + f"{', first token must be raw text' if not is_first_token_raw_text else ''}"
                          + f"{', second token must be HTML br-tag' if not has_html_br_tag_as_second_token else ''}. "
                          + f"cell={cell.children}",
                          file=sys.stderr)
        else:
            print(f"error: code {os.path.basename(__file__)} is written to require br-tag, please re-code it", file=sys.stderr)

        if button_sequence:
            result = ButtonSequence(button_sequence, tablerow.line_number)

        return result

    def extract_rawtext(self, rawtext):
        result = self.extract_button_sequence(rawtext.content)
        return result

    def extract_button_sequence(self, text):
        """
        "SHIFT + B1" => "SHIFT", "B1"
        "SHIFT + B1 (Long press)" => "SHIFT", "B1"
        "SHIFT + B1 or B2" => "SHIFT", "B1", "B2"
        "LEGENDARY" => []
        "B[1-8]" => "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8"
        "B[1-3,5]" => "B1", "B2", "B3", "B5"
        """
        sequence = [text]

        # Split the sequence
        for separator in self.separators:
            separates = []
            for element in sequence:
                element = element.split(separator)
                separates = separates + element
            sequence = separates

        # Strip whitespace from beginning and end
        sequence = list(map(str.strip, sequence))

        filtered = []
        poisoned = False
        patterns = self.button_patterns.keys()
        short_names = list(self.button_patterns.values())

        # Check each button in the sequence of controls
        for element in sequence:
            # constrain overall result to element's presence in recognized patterns
            match_results = list(map(lambda pattern: pattern.search(element), patterns))

            # Keep a found button sequence if it matches an expected button pattern.
            # Count matches (non-None) to ensure this is a valid button.
            match_count = len(match_results) - Counter(match_results)[None]

            if match_count > 0:
                if match_count > 1:
                    print(f"error: unexpected multiple-match count of {match_count} for element, \"{element}\"",
                          file=sys.stderr)
                match_index = self.find_first_non_null_index(match_results)
                short_name = short_names[match_index]
                filtered = filtered + [{element: short_name}]
            else:
                if DEBUG_LOG_EXTRACT:
                    print(f"could not find \"{element}\". Poisoning \"{sequence}\"", file=sys.stderr)
                self.could_not_find = self.could_not_find + [element]
                poisoned = True

        # Discard the sequence if one or more of the documented buttons does not match the list of valid button
        # patterns.
        if poisoned:
            sequence = []
        else:
            sequence = filtered

        result = sequence
        return result

    def find_first_non_null_index(self, a_list):
        return next((i for i, x in enumerate(a_list) if x is not None), -1)
