import re
import sys

import mistletoe
from mistletoe import markdown_renderer, ast_renderer
from mistletoe.block_token import BlockToken, Heading, Paragraph, SetextHeading
from mistletoe.markdown_renderer import MarkdownRenderer
from mistletoe.span_token import InlineCode, RawText, SpanToken

from extract_md import ButtonSequence

# For debugging parsing
DEBUG_LOG_MODIFY = True

# TODO Search also for <br/>
HTML_BREAK_PATTERN = r"<br>"
IMAGE_EXTENSION = "png"

def format_markdown(markdown_filename):
    formatter = FormatMarkdown(markdown_filename)
    return formatter.formatted


def write_markdown(md_out_file, image_out_path, md_in_file, button_sequences: [ButtonSequence]):
    print("write_markdown ... yeah")
    # TODO

    seqs = iter(button_sequences)
    seq = next(seqs)

    line_count = 0
    with open(md_in_file, "r") as fin:
        with open(md_out_file, "w") as fout:
            for line in fin:
                line_count += 1

                if seq.line_number == line_count:
                    # alter the line
                    # line = line.replace("<br>", "<br> CAT", 1)
                    line = replace_image_in_markdown(line, f"{image_out_path}/{seq.basename}.{IMAGE_EXTENSION}")

                    # Prepare for the next opportunity to mutate a button sequence
                    try:
                        seq = next(seqs)
                    except StopIteration:
                        pass

                fout.write(line)


def replace_image_in_markdown(line, new_image_path):
    # RegEx explanation:
    # Replace the entire image link, and capture (as '\1', etc.):
    # 1. the image label, if any, and not any extra ']' later in the line
    # 2. the image path, and not any extra ')' later in the line
    # 3. the rest of the line, after the image link
    replacement_pattern = r"!\[(.*?)\]\((.+?)\)(.+)"

    # TODO: Abort if <br> not found

    # IN: B1 <br> ![](img) | desc
    # OUT: 'B1 ', ' ![](img) | desc'
    split_lines = re.split(HTML_BREAK_PATTERN, line)

    if len(split_lines) <= 1:
        if DEBUG_LOG_MODIFY:
            temp = line.strip("\n")
            print(f"ignore unusual line, missing br-tag: \"{temp}\"", file=sys.stderr)
        return line

    modified_lines = []
    for segment in split_lines:
        # IN: ' ![](img) | desc'
        # OUT: ' ![](new_img)'
        modified_line = re.sub(replacement_pattern, fr"![\1]({new_image_path})\3", segment)
        modified_lines.append(modified_line)

    # Join the modified lines with '<br>' as separator
    # IN: 'B1 ', ' ![](new_img) | desc'
    # OUT: B1 <br> ![](new_img) | desc
    return HTML_BREAK_PATTERN.join(modified_lines)



class FormatMarkdown:
    """
    Expands tables with appropriate whitespace.
    Removes extraneous whitespace around bullets.
    """
    formatted: str = None

    def __init__(self, markdown_filename):
        with open(markdown_filename, "r") as fin:
            with MarkdownRenderer(normalize_whitespace=True) as renderer:
                document = mistletoe.Document(fin)
                self.formatted = renderer.render(document)
