from pathlib import Path

import mistletoe
from mistletoe.block_token import Paragraph, TableCell, TableRow, Table
from mistletoe.markdown_renderer import MarkdownRenderer, BlankLine
from mistletoe.token import Token

from button_sequence import ButtonSequence
from modify_md import validate_files
from util import ImageOpt, print_markdown_tree  # noqa: F401

# For debugging parsing
DEBUG_LOG_SEQS = True


def write_seqs_markdown(md_out_file, image_out_path, md_in_file, button_sequences: [ButtonSequence], opt: ImageOpt):
    """

    :param md_out_file: Destination of collected button sequences, in Markdown
    :param image_out_path: 
    :param md_in_file: Source of button_sequences. Only used for file-overwrite protection.
    :param button_sequences: 
    :param opt: 
    :return: 
    """
    validate_files(md_in_file, md_out_file)

    if not button_sequences:
        if DEBUG_LOG_SEQS:
            print("Not writing sequences Markdown, no data")
        return

    with (open(md_out_file, "w") as fout):
        with MarkdownRenderer(max_line_length=99) as renderer:
            ButtonSequence.init_description(button_sequences, renderer)
            print(button_sequences)
            
            # TODO Derive category from description text, mapping keywords to known categories, using the best match
            
            text = Path("test_seqs.md").read_text()
            doc = mistletoe.Document(text)
            print_markdown_tree(doc.children)
            print("rendering ...")
            md = renderer.render(doc)
            print(md)

            # #####
            print("next ...")

            doc = mistletoe.Document("")
            
            doc.children.extend(create_title_list())

            headers = to_table_line(["Thing1", "Thing2", "Thing3"])
            header_aligns = to_table_line(["--"], 3)
            header_text = headers + header_aligns
            columns = ["SHIFT + B1 <br> ![label-1.1](link-1.1) <br> Cell 1.1 text",
                       "SHIFT + B2 <br> ![label-2.1](link-2.1) <br> Cell 2.1 text",
                       "SHIFT + B3 <br> ![label-3.1](link-3.1) <br> Cell 3.1 text"]
            rows = [columns[0],
                    "SHIFT + B1 <br> ![label-1.2](link-1.2) <br> Cell 1.2 text",
                    "SHIFT + B1 <br> ![label-1.3](link-1.3) <br> Cell 1.3 text"]
            row_text = to_table_line(rows)
            table_text = header_text + row_text

            doc.children.append(create_table(table_text))

            doc.children.extend(create_title_list("title 2"))
            doc.children.append(create_table(table_text))

            doc.children.extend(create_title_list("title 3"))
            doc.children.append(create_table(table_text))

            # print_markdown_tree(doc.children)
            print("rendering ...")
            md = renderer.render(doc)
            # print(md)

            fout.write(md)


def create_title_list(text="title", line_number=1):
    return [create_blankline(), create_paragraph(text, line_number), create_blankline()]


def create_table(table_text):
    table = Table((table_text, 1))
    table.line_number = 1
    return table


def to_table_line(elements:[str], column_count = 0) -> [str]:
    cc = 1
    if column_count:
        cc = column_count
    return ["|".join(elements * cc) + "\n"]


def create_paragraph(text, line_number=1) -> [Token]:
    """
    
    :param text: 
    :param line_number: 
    :return: 
    <mistletoe.block_token.Paragraph with 1 child line_number=2 at 0x101da5890>
    |   <mistletoe.span_token.RawText content='Title 1' at 0x101da5610>
    """
    lines = [text + " \n"]
    result = Paragraph(lines)

    # TRICKY: line_number is required and is not set in the constructor, only in block_token.tokenize()
    result.line_number = line_number

    return result


def create_blankline():
    result = BlankLine([""])
    result.line_number = 1
    return result


def create_cell(text: str, line_number=1) -> [TableCell]:
    """

    :param line_number: 
    :param text: 
    :param param: 
    :return: 
    <mistletoe.block_token.TableCell with 7 children line_number=6 align=0 at 0x105548ad0>
    |   <mistletoe.span_token.RawText content='SHIFT + B1 ' at 0x10554b5d0>
    |   <mistletoe.span_token.HtmlSpan content='<br>' at 0x10554b610>
    |   <mistletoe.span_token.RawText content=' ' at 0x10554b4d0>
    |   <mistletoe.span_token.Image with 1 child src='link-1.1' title='' at 0x10554b950>
    |   |   <mistletoe.span_token.RawText content='label-1.1' at 0x105549110>
    |   <mistletoe.span_token.RawText content=' ' at 0x10554b9d0>
    |   <mistletoe.span_token.HtmlSpan content='<br>' at 0x10554b890>
    |   <mistletoe.span_token.RawText content=' Cell 1.2 text' at 0x10554bc10>
    """

    lines = [text + " \n"]
    result = TableCell(lines)

    # TRICKY: line_number is required and is not set in the constructor, only in block_token.tokenize()
    result.line_number = line_number

    return result


def create_row(row_text, line_number=1) -> TableRow:
    result = TableRow(row_text)
    result.line_number = line_number
    return result
