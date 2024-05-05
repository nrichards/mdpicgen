import mistletoe
from mistletoe.block_token import BlockToken, Heading, Paragraph, SetextHeading
from mistletoe.span_token import InlineCode, RawText, SpanToken
from mistletoe.markdown_renderer import MarkdownRenderer

from modify_md import validate_files
from button_sequence import ButtonSequence
from util import ImageOpt, print_markdown_tree

# For debugging parsing
DEBUG_LOG_SEQS = True


# TODO Format the output file with mistletoe


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

    with open(md_out_file, "w") as fout:
        with MarkdownRenderer() as renderer:
            text = """
Title 1

| Heading 1 | Heading 2 | Heading 3 |
| :--: | -- | -- |
| SHIFT + B1 <br> ![label-1.1](link-1.1) <br> Cell 1.2 text | SHIFT + B3 <br> ![label-1.3](link-1.3) <br> Cell 1.3 text | SHIFT + B4 <br> ![label-1.4](link-1.4) <br> Cell 1.4 text |
| SHIFT + B2 <br> ![label-2.1](link-2.1) <br> Cell 2.2 text | SHIFT + B2 <br> ![label-2.1](link-2.1) <br> Cell 2.3 text | SHIFT + B4 <br> ![label-2.4](link-2.4) <br> Cell 2.4 text |

Title 2

| Heading 2.1 | Heading 2.2 | 
| :--: | -- | 
| SHIFT + B6 <br> ![label-1.1](link-1.1) <br> Cell 1.2 text | SHIFT + B7 <br> ![label-1.7](link-1.1) <br>Cell 1.3 text |
| SHIFT + B6 <br> ![label-2.1](link-2.1) <br> Cell 2.2 text | SHIFT + B7 <br> ![label-2.7](link-2.1) <br>Cell 2.3 text |
"""
            doc = mistletoe.Document(text)
            print_markdown_tree(doc.children)

            print("rendering ...")
            md = renderer.render(doc)
            print(md)
            fout.write(md)



def update_text(token: SpanToken):
    """Update the text contents of a span token and its children.
    `InlineCode` tokens are left unchanged."""
    if isinstance(token, RawText):
        token.content = token.content.replace("mistletoe", "The Amazing mistletoe")

    if not isinstance(token, InlineCode) and hasattr(token, "children"):
        for child in token.children:
            update_text(child)

def update_block(token: BlockToken):
    """Update the text contents of paragraphs and headings within this block,
    and recursively within its children."""
    if isinstance(token, (Paragraph, SetextHeading, Heading)):
        for child in token.children:
            update_text(child)

    for child in token.children:
        if isinstance(child, BlockToken):
            update_block(child)


# def generate_markdown_table(data):
#     """Generates markdown table with 4 columns from a list of data.
#   
#     Args:
#         data: A list of lists, where each inner list represents a row in the table.
#   
#     Returns:
#         A string containing the markdown representation of the table.
#     """
#     markdown = ""
#     table = Table(headings=["Column 1", "Column 2", "Column 3", "Column 4"])
# 
#     for row in data:
#         if len(row) != 4:
#             raise ValueError("Each row in data must have 4 elements.")
#         table_row = TableRow([TableCell(c) for c in row])
#         table.add_child(table_row)
# 
#     markdown += table.render()
#     return markdown
# 
# # Sample data for the table
# data = [
#     ["Data 1-1", "Data 1-2", "Data 1-3", "Data 1-4"],
#     ["Data 2-1", "Data 2-2", "Data 2-3", "Data 2-4"],
#     # Add more rows as needed
# ]
# 
# # Generate markdown string
# markdown_string = generate_markdown_table(data)
# 
# # Write markdown string to a file
# with open("output.md", "w") as f:
#     f.write(markdown_string)
# 
# # Render markdown to HTML (optional)
# # renderer = Markdown()
# # html_output = renderer.render(markdown_string)
# # print(html_output)