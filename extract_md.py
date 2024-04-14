from typing import Dict

import mistletoe
from mistletoe import markdown_renderer, ast_renderer
from mistletoe.block_token import BlockToken, Heading, Paragraph, SetextHeading, Table, TableRow, TableCell
from mistletoe.markdown_renderer import MarkdownRenderer
from mistletoe.span_token import InlineCode, RawText, SpanToken
import csv
import io

# A table header label indicating its cells should be extracted. Must be the first column.
HEADER_TRIGGER_KEY = "Button".lower()

# TODO
# Keep line-number of finding
# E.g. {284 : "MODE PLAY + SYSTEM + turn dial", 285: "SYSTEM + turn dial"}


# TODO - handle Image. This is a Cell. The children form a button sequence where we WANT to have images.
# 0 = {RawText} <mistletoe.span_token.RawText content='SHIFT + MODE PLAY ' at 0x1053bd490>
# 1 = {HtmlSpan} <mistletoe.span_token.HtmlSpan content='<br>' at 0x1053bd4d0>
# 2 = {RawText} <mistletoe.span_token.RawText content=' ' at 0x1053bd550>
# 3 = {Image} <mistletoe.span_token.Image with 0 children src='./manual_images/but/s_mplay.pn'...+1 title='' at 0x1053bd590>


def extract_buttons(md_file):
    extractor = ExtractButtonsFromMarkdown(md_file)
    return extractor.buttons


class ExtractButtonsFromMarkdown:
    """
    Extracts button command sequences from tables in Markdown.
    """
    buttons: [[str]] = []  # [ [ "SHIFT", "B1"], [ "SEQ PLAY" ] ]

    button_pattern = []

    def __init__(self, markdown_filename):
        self.button_pattern = self.patterns_map_to_button_name()
        with open(markdown_filename, "r") as fin:
            with MarkdownRenderer(normalize_whitespace=True) as renderer:
                document = mistletoe.Document(fin)
                result = self.extract_document(document)
                self.buttons = result

    def patterns_map_to_button_name(self) -> {str, str}:
        """
        String patterns of button control found in a document, and their canonical names.
        Case-insensitive.
        Pipe (|) separates the word and its value.
        """
        pattern_to_canonical_button_name = """
SHIFT | s
1 | 1
2 | 2
3 | 3
4 | 4
5 | 5
6 | 6
7 | 7
turn dial | dial
dial | dial
NO | n
OK | o
LOOPER PLAY | lplay
LOOPER REC | lr
REC | lr
LOOPER STOP | ls
MODE PLAY | mplay
PARAM | param
SYSTEM | sys
SEQ PLAY | splay
"""
        return self.load_constants_from_csv(pattern_to_canonical_button_name)

    def load_constants_from_csv(self, csv_data: str, delimiter="|") -> {str, str}:
        constants = {}
        for row in csv.reader(io.StringIO(csv_data), delimiter=delimiter):
            if not row:
                continue
            key, value = row
            constants[key] = value
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
                if extract:
                    result = result + [extract]
                else:
                    print("no extract")
        return result

    def is_button_table(self, table) -> bool:
        label = table.header.children[0].children[0]
        if type(label) is RawText:
            if label.content.lower().startswith(HEADER_TRIGGER_KEY):
                return True
        return False

    def extract_tablerow(self, tablerow: mistletoe.block_token.TableRow) -> [str]:
        result = []

        # first cell: assumes first column of table
        cell = tablerow.children[0]

        # first token with user content: assumes "B1 <br> ![](path-to-image)", and extracts "B1"
        token = cell.children[0]
        if type(token) is RawText:
            result = result + self.extract_rawtext(token)

        return result

    def extract_rawtext(self, rawtext):
        result = self.extract_button_sequence(rawtext.content)
        return result

    def is_valid_sequence(self, candidates):
        return False
        # NICk
        # for candidate in candidates:
        #     if candidate:
        #         case 'B1':
        #         case 'B2':
        #             return True

    def extract_button_sequence(self, text):
        # Split the sequence
        result = text.split("+")

        # Split based on atypical "or"
        or_sequence = []
        for element in result:
            element = element.split("or")
            or_sequence = or_sequence + element
        result = or_sequence

        # Remove (long press)
        # TODO

        # Strip whitespace from beginning and end
        result = list(map(str.strip, result))

        # if not self.is_valid_sequence(result):
        #     return []

        return result


# table = mistletoe.markdown("""
# | Name | Age |
# |---|---|---|
# | Alice | 25 |
# | Bob | 30 |
# """, markdown_renderer.MarkdownRenderer)

# table = mistletoe.markdown("""
# | Name | Age |
# |---|---|---|
# | Alice | 25 |
# | Bob | 30 |
# """, ast_renderer.AstRenderer)
#
# # Modify the contents of the table
# # table.children[1].children[1].children[0].text = "26"
#
# markdown_text = mistletoe.markdown(table, markdown_renderer.MarkdownRenderer)
#
# # Print the modified Markdown text
# print(markdown_text)


"""
SHIFT | s
1 | 1
2 | 2
3 | 3
4 | 4
5 | 5
6 | 6
7 | 7
turn dial | dial
dial | dial
NO | n
OK | o
LOOPER PLAY | lplay
LOOPER REC | lr
REC | lr
LOOPER STOP | ls
MODE PLAY | mplay
PARAM | param
SYSTEM | sys
SEQ PLAY | splay
"""

"""
1 | 1
1 (Long press) | 1

2 | 2
2 (Long press) | 2
2 in SEQ CFG sub-mode (Long press) | 2

3 | 3
3 (Long press) | 3
3 in SEQ CFG sub-mode (Long press) | 3

4 | 4
4 (Long press) | 4

5 | 5
5 (Long press) | 5

6 | 6
6 (Long press) | 6

7 | 7
7 (Long press) | 7

8 | 8

B 7
 or 8

B 7 or 8 + turn dial

B[1-8]

B[1-8] (Long press), then PARAM

B[1-8] + NO / OK

B[1-8] + PARAM + turn dial

B[1-8] + turn dial

Dial

LOOPER PLAY

LOOPER PLAY + NO or OK

LOOPER PLAY + [1-5]

LOOPER PLAY + [1-5] + turn dial

LOOPER REC + LOOPER PLAY

LOOPER STOP

MODE PLAY

MODE PLAY (RECALL) + B[1-8]

MODE PLAY (RECALL) + B[1-8] + turn dial

MODE PLAY (RECALL) + [1-8]

MODE PLAY + PARAM + turn dial

MODE PLAY + SYSTEM + turn dial

MODE PLAY + turn dial

NO
NO (<)

NO or OK button while selecting a session

OK
OK (>)

PARAM

PARAM (Long press)

PARAM + NO

PARAM + [1-3]

PARAM + turn dial

Press B[1-8] while booting

REC

REC + LOOPER PLAY

REC + NO

REC + OK

REC + PARAM

REC + SEQ PLAY

REC + SEQ PLAY + turn dial

REC + [1-3, 7,8]

REC + turn dial

SEQ PLAY

SEQ PLAY + B[1-8] (Primary pattern) + B[1-8] (2nd pattern) in any sub-mode

SEQ PLAY + NO / OK

SEQ PLAY + [1-8]

SEQ PLAY + [1-8] + turn dial

SEQ PLAY + [1-8] , [1-8]...

SHIFT

SHIFT + Button 7

SHIFT + Button 8

SHIFT + LOOPER PLAY

SHIFT + LOOPER PLAY + [1-3] button

SHIFT + LOOPER PLAY + turn dial

SHIFT + LOOPER REC

SHIFT + LOOPER STOP

SHIFT + Looper Stop

SHIFT + MODE PLAY

SHIFT + MODE PLAY + turn dial

SHIFT + NO

SHIFT + NO + OK

SHIFT + OK
SHIFT + OK (Before loading)

SHIFT + PARAM

SHIFT + REC

SHIFT + REC (Long press)

SHIFT + REC + B[1-3]

SHIFT + SEQ PLAY +  NO / OK

SHIFT + SEQ PLAY + turn dial

SHIFT + SYSTEM

SHIFT + turn dial <br> clockwise almost to end

SYSTEM

SYSTEM + PARAM + turn dial

SYSTEM + [1-8]

SYSTEM 

Turn dial

[1-8] button
"""
