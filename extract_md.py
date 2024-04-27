import csv
import io
import re
import sys
from collections import Counter
from pathlib import Path

from mistletoe.block_token import Table, TableRow, Document, TableCell
from mistletoe.markdown_renderer import MarkdownRenderer
from mistletoe.span_token import RawText, HtmlSpan

from constants import HTML_BREAK_PATTERN, SHORT_NAME_INFIX_SEPARATOR, COMMENT_KEY, SEPARATOR_VALUE_WRAPPER, \
    SEPARATOR_KEY, TABLE_HEADER_KEY, PATTERN_FILE_DELIMITER, DIGITS_MACRO_NAME

# For debugging parsing
DEBUG_LOG_EXTRACT = True

EXTRACT_CAPTURE_GROUP_INDEX = 1


def extract_button_sequences(md_file, but_pat_file) -> ["ButtonSequence"]:
    """
    Extract button command sequences from Markdown following a set of patterns.

    :param md_file: Markdown file formatted with well-known button sequences in special tables
    :param but_pat_file: Text file mapping regular expressions to buttons, and defining separator patterns
    :return: List of dictionaries mapping recognized button names, as written in the input Markdown, to short names
    which are used as compound layer names in basenames of generated image files illustrating the button sequence
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
    """
    Containers button command sequence data.
    """
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
        Extracts a list of button sequence strings, mapping to shortnames, from an input list of ButtonSequences.
        """
        if button_sequences and type(button_sequences[0]) is not ButtonSequence:
            print(
                f"error: can't transform extracted mapping to sequence list, "
                f"unsupported type: {type(button_sequences[0])}")
            return

        result = [seq.sequence_mapping for seq in button_sequences]

        return result


class ExtractButtonsFromMarkdown:
    """
    Extracts button command sequences from tables in Markdown.
    """

    buttons: [[]] = []
    """ [ [{'SHIFT': 's'}, {'SEQ PLAY': 'splay'}, {'turn dial': 'd'}], ...] -- for example """
    button_sequences: [ButtonSequence] = []
    """ Extracted sequences, also contains line numbers """
    could_not_find = []
    """ Sequences not matched by the patterns """

    # Options
    require_br_tag = True  # "SHIFT + SEQ PLAY + turn dial <br> ..." -- default constraint

    def __init__(self, markdown_filename, button_pattern_file):
        self.button_patterns = self.patterns_map_to_button_name(button_pattern_file)
        self.separators = self.patterns_to_separators(button_pattern_file)
        self.header = self.patterns_to_header(button_pattern_file)

        with open(markdown_filename, "r") as fin:
            with MarkdownRenderer(normalize_whitespace=True) as _:
                document = Document(fin)

                # Extract buttons, following constraints and patterns, and store results
                result = self.extract_document(document)
                self.button_sequences = result
                self.buttons = ButtonSequence.to_sequence_mapping_list(self.button_sequences)

    @staticmethod
    def patterns_map_to_button_name(button_pattern_file) -> {str, str}:
        """
        String patterns of button control found in a document,
        and their canonical names.
        Patterns use regular expressions.
        Case-insensitive, specially handled elsewhere by code.
        Equals (=) separates the word and its value. See BUTTON_PATTERN_DELIMITER.
        """
        pattern_to_canonical_button_name = Path(button_pattern_file).read_text()

        return ExtractButtonsFromMarkdown.load_constants_from_csv(pattern_to_canonical_button_name)

    @staticmethod
    def patterns_to_separators(button_pattern_file) -> [str]:
        button_pattern_data = Path(button_pattern_file).read_text()
        return ExtractButtonsFromMarkdown.load_values_from_csv(button_pattern_data, SEPARATOR_KEY)

    @staticmethod
    def patterns_to_header(button_pattern_file):
        button_pattern_data = Path(button_pattern_file).read_text()
        values = ExtractButtonsFromMarkdown.load_values_from_csv(button_pattern_data, TABLE_HEADER_KEY)
        result = values[0].strip()
        return result

    @staticmethod
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

    @staticmethod
    def load_values_from_csv(button_pattern_file, find_key, delimiter=PATTERN_FILE_DELIMITER):
        result = [
            row[1].strip().strip(SEPARATOR_VALUE_WRAPPER)
            for row in csv.reader(io.StringIO(button_pattern_file), delimiter=delimiter)
            if row and row[0].startswith(find_key)
        ]

        return result

    def extract_document(self, doc: Document) -> [ButtonSequence]:
        """
        Transforms a Markdown into an array of recognized sequences.
        :param doc: Any Markdown
        :return: Matches for structure and text pattern criteria
        """
        result = [
            sequence
            for token in doc.children if type(token) is Table
            for sequence in self.extract_table(token)
        ]

        return result

    def extract_table(self, table: Table) -> [ButtonSequence]:
        result = []

        if self.is_button_table(table, self.header.lower()):
            extracted = [self.extract_tablerow(child) for child in table.children]
            result = [e for e in extracted if e]

        return result

    @staticmethod
    def is_button_table(table, header) -> bool:
        label = table.header.children[0].children[0]
        return type(label) is RawText and label.content.lower().startswith(header)

    def extract_tablerow(self, tablerow: TableRow) -> ButtonSequence:
        """
        Extracts valid data from cells in first column of table.
         
        :param tablerow: candidate data needing examination
        :return: A ButtonSequence object or None if no valid data is found
        """
        result = None
        cell = tablerow.children[0]

        valid_token, mismatch = self.validate_cell_structure(cell)

        if valid_token:
            sequence_map = self.extract_rawtext(valid_token)

            if sequence_map:
                result = ButtonSequence(sequence_map, tablerow.line_number)
        elif mismatch and DEBUG_LOG_EXTRACT:
            print(f"ignored cell: {mismatch}", file=sys.stderr)

        return result

    @staticmethod
    def validate_cell_structure(cell: TableCell) -> (RawText, str):
        """Extract the first token with content. Presumes e.g. "B1 <br> ![](path-to-image)", and extracts "B1". 
        Also supports no-image.
        
        Return: 
            Tuple: [0] = optional RawText success element, [1] = optional descriptive string mismatch text
        """
        mismatches = []

        has_enough_children = len(cell.children) > 1
        mismatches.append('needs more children') if not has_enough_children else True

        is_first_token_raw_text = len(cell.children) > 0 and type(cell.children[0]) is RawText
        mismatches.append('first token must be raw text') if not is_first_token_raw_text else True

        has_html_br_tag_as_second_token = \
            (has_enough_children and
             type(cell.children[1]) is HtmlSpan and
             re.match(HTML_BREAK_PATTERN, cell.children[1].content, re.IGNORECASE))
        mismatches.append('second token must be HTML br-tag') if not has_html_br_tag_as_second_token else True

        if not mismatches:
            result = (cell.children[0], None)
        else:
            result = (None, ", ".join(mismatches) + f": {cell.children}")

        return result

    def extract_rawtext(self, rawtext) -> [{str: str}]:
        result = self.extract_valid_sequence_map(rawtext.content)
        return result

    def extract_valid_sequence_map(self, text: str) -> [{str: str}]:
        """
        Transform a raw text string to a list of valid presentation strings mapped to their encoded names.
        Discard entire sequence if any element in the sequence is not valid.

        Args:
            text: Whitespace padded raw text extracted. Assume this is from a structurally-matching table cell.
        
        Returns:
            List of validated mappings between presentation and encoding, or empty list.
            
        Example:
            text = 'SHIFT + SEQ PLAY + turn dial '
            return = [{'SHIFT': 's'}, {'SEQ PLAY': 'splay'}, {'turn dial': 'd'}]
        """

        candidate_sequence = self.separate_rawtext(text, self.separators)
        validating_patterns = self.button_patterns.keys()
        valid_names = list(self.button_patterns.values())

        poison, valid_sequence = self.filter_sequence(candidate_sequence, valid_names, validating_patterns)

        if not poison:
            result = valid_sequence
        else:
            if DEBUG_LOG_EXTRACT:
                print(f"could not match \"{poison}\", poisoning sequence \"{candidate_sequence}\"", file=sys.stderr)
            self.could_not_find.append(poison)
            result = []

        return result

    @staticmethod
    def filter_sequence(candidate_sequence, valid_names, validating_patterns) -> (str, [str]):
        valid_sequence = []
        poison = None
        for element in candidate_sequence:
            valid_element = ExtractButtonsFromMarkdown.match_element(element, valid_names, validating_patterns)

            if valid_element:
                valid_sequence.append(valid_element)
            else:
                poison = element
                break
        return poison, valid_sequence

    @staticmethod
    def match_element(element, valid_names, validating_patterns) -> {str: str}:
        # constrain overall result to element's presence in recognized patterns
        match_results = list(map(lambda p: p.search(element), validating_patterns))

        # Keep a found button sequence if it matches an expected button pattern.
        # Count matches (non-None) to ensure this is a valid button.
        match_count = len(match_results) - Counter(match_results)[None]

        result = {}
        match match_count:
            case 0:
                pass
            case 1:
                match_index = ExtractButtonsFromMarkdown.find_first_non_null_index(match_results)
                
                pattern_match = match_results[match_index]
                element_group = ExtractButtonsFromMarkdown.get_capture_group(element, pattern_match)
                
                short_name = valid_names[match_index]
                macro_expanded = ExtractButtonsFromMarkdown.macro_expand_short_name(element_group, short_name)
                result = {element: macro_expanded}
            case _:
                print(f"error: unexpected multiple matches ({match_count}) for element \"{element}\", "
                      f"check the pattern file",
                      file=sys.stderr)

        return result

    @staticmethod
    def get_capture_group(element, pattern_match) -> str:
        """ Extract only the desired capture group, if specified. We use the first (1) group.
        Useful to exclude e.g. the "2" from "B[1-8] (2nd pattern) in any sub-mode".
        
        Returns: first (EXTRACT_CAPTURE_GROUP_INDEX) capture group, or the whole match if no group.
        """
        return pattern_match.group(EXTRACT_CAPTURE_GROUP_INDEX) if pattern_match.lastindex else element

    @staticmethod
    def separate_rawtext(text, separators):
        """Split the text to a sequence, stripping padding."""
        sequence = [text]

        for separator in separators:
            separates = []
            for element in sequence:
                element = element.split(separator)
                separates = separates + element
            sequence = separates

        sequence = ExtractButtonsFromMarkdown.strip_whitespace(sequence)
        return sequence

    @staticmethod
    def strip_whitespace(sequence):
        return list(map(str.strip, sequence))

    @staticmethod
    def find_first_non_null_index(a_list):
        return next((i for i, x in enumerate(a_list) if x is not None), -1)

    @staticmethod
    def macro_expand_short_name(element, short_name) -> str:
        """Replace recognized macros found in short_name with the results from their execution.
        """
        temp = short_name

        if DIGITS_MACRO_NAME in temp:
            replacement = ExtractButtonsFromMarkdown.extract_digit_ranges(element)
            temp = temp.replace(DIGITS_MACRO_NAME, replacement)

        result = temp
        return result

    @staticmethod
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
