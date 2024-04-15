import csv
import io
import re
from collections import Counter
from pathlib import Path

import mistletoe
import sys
from mistletoe.block_token import Table
from mistletoe.markdown_renderer import MarkdownRenderer
from mistletoe.span_token import RawText, HtmlSpan

SEPARATOR_OR = " or "
SEPARATOR_PLUS = "+"

# A table header label indicating its cells should be extracted. Must be the first column.
HEADER_TRIGGER_KEY = "Button".lower()
BUTTON_PATTERN_DELIMITER = "="

# TODO
# Keep line-number of finding
# E.g. {284 : "MODE PLAY + SYSTEM + turn dial", 285: "SYSTEM + turn dial"}


# TODO - handle Image. This is a Cell. The children form a button sequence where we WANT to have images.
# 0 = {RawText} <mistletoe.span_token.RawText content='SHIFT + MODE PLAY ' at 0x1053bd490>
# 1 = {HtmlSpan} <mistletoe.span_token.HtmlSpan content='<br>' at 0x1053bd4d0>
# 2 = {RawText} <mistletoe.span_token.RawText content=' ' at 0x1053bd550>
# 3 = {Image} <mistletoe.span_token.Image with 0 children src='./manual_images/but/s_mplay.pn'...+1 title='' at 0x1053bd590>


def extract_buttons(md_file, but_pat_file):
    extractor = ExtractButtonsFromMarkdown(md_file, but_pat_file)
    print(f"rejected: {len(extractor.could_not_find)}")
    return extractor.buttons


class ExtractButtonsFromMarkdown:
    """
    Extracts button command sequences from tables in Markdown.
    """
    buttons: [[str]] = []  # [ [ "SHIFT", "B1"], [ "SEQ PLAY" ] ] -- for example

    require_br_tag = True  # "SHIFT + B1 <br> ..." -- default constraint

    could_not_find = []

    def __init__(self, markdown_filename, button_pattern_file):
        self.button_patterns = self.patterns_map_to_button_name(button_pattern_file)
        self.separators = [SEPARATOR_PLUS, SEPARATOR_OR]

        with open(markdown_filename, "r") as fin:
            with MarkdownRenderer(normalize_whitespace=True) as renderer:
                document = mistletoe.Document(fin)

                # Extract buttons, following constraints and patterns, and store results
                result = self.extract_document(document)
                self.buttons = result

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

    def load_constants_from_csv(self, csv_data: str, delimiter=BUTTON_PATTERN_DELIMITER) -> {re.Pattern, str}:
        """
        Return a dict of regular expressions and their equivalent string identifiers.

        To be used to match button names to short-form, well-known button identifiers.
        """
        constants = {}
        for row in csv.reader(io.StringIO(csv_data), delimiter=delimiter):
            if not row:
                continue
            if row[0].startswith("# "):
                continue

            key, value = row
            ks = key.strip()
            kre = re.compile(ks, re.IGNORECASE)
            constants[kre] = value.strip()
            # except ValueError as e:
            #     print(f"warning: ignoring pattern: {row}", file=sys.stderr)
            #     continue
        return constants

    def extract_document(self, doc) -> [[str]]:
        result = []
        for token in doc.children:
            if type(token) is Table:
                result = result + self.extract_table(token)
        return result

    def extract_table(self, table: mistletoe.block_token.Table) -> [[str]]:
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
            if label.content.lower().startswith(HEADER_TRIGGER_KEY):
                return True
        return False

    def extract_tablerow(self, tablerow: mistletoe.block_token.TableRow) -> [str]:
        result = []
        button_sequence = []

        # first cell: assumes first column of table
        cell = tablerow.children[0]

        # first token with user content: assumes "B1 <br> ![](path-to-image)", and extracts "B1"
        token = cell.children[0]
        if type(token) is RawText:
            button_sequence = self.extract_rawtext(token)

        # constrain to require br-tag
        if (button_sequence and
                self.require_br_tag and
                len(cell.children) > 1 and
                type(cell.children[1]) is HtmlSpan):
            result = result + button_sequence

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
        TODO: "B[1-8]" => "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8" 
        TODO: "B[1-3,5]" => "B1", "B2", "B3", "B5"
         
        :param text: 
        :return: 
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
        for element in sequence:
            # constrain overall result to element's presence in recognized patterns
            # print(f"checking \"{element}\" ...")
            match_results = list(map(lambda pattern: pattern.search(element), patterns))

            # count matches (non-None)
            match_count = len(match_results) - Counter(match_results)[None]

            if match_count > 0:
                filtered = filtered + [element]
            else:
                print(f"could not find \"{element}\". Poisoning \"{sequence}\"")
                self.could_not_find = self.could_not_find + [element]
                poisoned = True
        if poisoned:
            sequence = []
        else:
            sequence = filtered

        result = sequence

        return result
