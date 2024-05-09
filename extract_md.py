import re

import sys
from collections import Counter

from mistletoe.block_token import Table, TableRow, Document, TableCell, Heading
from mistletoe.markdown_renderer import MarkdownRenderer
from mistletoe.span_token import RawText, HtmlSpan

from button_sequence import ButtonSequence
from constants import HTML_BREAK_PATTERN, DIGITS_MACRO_NAME
from util import (extract_digit_ranges, strip_whitespace, find_first_non_null_index, print_markdown_tree, 
                  find_nearest_less_than_or_equal)
from patset import patterns_to_header, patterns_to_separators, patterns_map_to_button_name

# For debugging parsing
DEBUG_LOG_EXTRACT = False
DEBUG_LEVEL_DEEP = False

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
        self.button_patterns = patterns_map_to_button_name(button_pattern_file)
        self.separators = patterns_to_separators(button_pattern_file)
        self.header = patterns_to_header(button_pattern_file)

        with open(markdown_filename, "r") as fin:
            with MarkdownRenderer(normalize_whitespace=True) as _:
                document = Document(fin)
                
                if DEBUG_LOG_EXTRACT and DEBUG_LEVEL_DEEP:
                    print_markdown_tree(document.children)
    
                # Extract buttons, following constraints and patterns, and store results
                result = self.extract_document(document)
                self.button_sequences = result
                self.buttons = ButtonSequence.to_sequence_mapping_list(self.button_sequences)

    def extract_document(self, doc: Document) -> [ButtonSequence]:
        """
        Transforms a Markdown into an array of recognized sequences.
        :param doc: Any Markdown
        :return: Matches for structure and text pattern criteria
        """
        
        heading_lines = [(token.line_number, token.children[0].content) 
                         for token in doc.children if type(token) is Heading]
        
        result = [
            seq
            for token in doc.children if type(token) is Table
            for seq in self.extract_titled_table(token, heading_lines)
        ]

        return result

    def extract_titled_table(self, table: Table, heading_lines:[(int, str)]) -> (str, [ButtonSequence]):
        _, heading = find_nearest_less_than_or_equal(heading_lines, table.line_number)

        result = []

        if ExtractButtonsFromMarkdown.is_button_table(table, self.header.lower()):
            extracted = [self.extract_tablerow(child, heading) for child in table.children]
            result = [e for e in extracted if e]

        return result

    @staticmethod
    def is_button_table(table, header) -> bool:
        label = table.header.children[0].children[0]
        return type(label) is RawText and label.content.lower().startswith(header)

    def extract_tablerow(self, tablerow: TableRow, section_title) -> ButtonSequence:
        """
        Extracts valid data from cells in first column of table.
         
        :param section_title: 
        :param tablerow: candidate data needing examination
        :return: A ButtonSequence object or None if no valid data is found
        """
        result = None
        cell = tablerow.children[0]

        valid_token, mismatch = self.validate_cell_structure(cell)

        if valid_token:
            sequence_map, text = self.extract_rawtext(valid_token)

            if sequence_map:
                description_tablecell = tablerow.children[1]
                result = ButtonSequence(mapping=sequence_map, line_no=tablerow.line_number, text=text,
                                        section_title=section_title, description_tablecell=description_tablecell)
        elif mismatch and DEBUG_LOG_EXTRACT:
            print(f"ignored cell at {tablerow.line_number}: {mismatch}", file=sys.stderr)

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

    def extract_rawtext(self, rawtext) -> ([{str: str}], str):
        result = self.extract_valid_sequence_map(rawtext.content)
        return result, rawtext.content

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
                match_index = find_first_non_null_index(match_results)

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

        sequence = strip_whitespace(sequence)
        return sequence

    @staticmethod
    def macro_expand_short_name(element, short_name) -> str:
        """Replace recognized macros found in short_name with the results from their execution.
        """
        temp = short_name

        if DIGITS_MACRO_NAME in temp:
            replacement = extract_digit_ranges(element)
            temp = temp.replace(DIGITS_MACRO_NAME, replacement)

        result = temp
        return result
    