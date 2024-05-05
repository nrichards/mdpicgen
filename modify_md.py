import re
import sys
import os
import shutil

from mistletoe import Document
from mistletoe.markdown_renderer import MarkdownRenderer

from constants import HTML_BREAK_PATTERN, HTML_BREAK
from button_sequence import ButtonSequence
from util import ImageOpt

# For debugging parsing
DEBUG_LOG_MODIFY = True


def format_markdown(markdown_filename):
    formatter = FormatMarkdown(markdown_filename)
    return formatter.formatted


def write_markdown(md_out_file, image_out_path, md_in_file, button_sequences: [ButtonSequence], opt: ImageOpt):
    validate_files(md_in_file, md_out_file)

    if not button_sequences:
        shutil.copyfile(md_in_file, md_out_file)
        return

    with open(md_in_file, "r") as fin:
        with open(md_out_file, "w") as fout:
            write_updated_markdown(button_sequences, fin, fout, image_out_path, opt)


def validate_files(md_in_file, md_out_file):
    if os.path.normpath(md_in_file) == os.path.normpath(md_out_file):
        raise FileExistsError(f"Cannot write to same file that is being read from: \"{md_in_file}\"")


def write_updated_markdown(button_sequences, fin, fout, image_out_path, opt):
    seqs = iter(button_sequences)
    seq = next(seqs)
    line_count = 0
    for in_line in fin:
        line_count += 1

        out_line = in_line
        if seq.line_number == line_count:
            # alter the line
            out_line = update_or_replace_image_in_markdown(
                in_line, f"{image_out_path}/{seq.basename}.{opt.extension()}")

            # Prepare for the next opportunity to mutate a button sequence
            try:
                seq = next(seqs)
            except StopIteration:
                pass

        fout.write(out_line)
        if DEBUG_LOG_MODIFY:
            print("OUT: " + out_line.strip('\n'), file=sys.stderr)


def update_or_replace_image_in_markdown(line, new_image_path):
    # RegEx explanation:
    # Replace the entire image link, and capture (as '\1', etc.):
    # 1. the image label, if any, and not any extra ']' later in the line
    # 2. the image path, and not any extra ')' later in the line
    # 3. the rest of the line, after the image link
    replacement_pattern = r"!\[(.*?)\]\((.+?)\)(.+)"

    # IN: B1 <br> ![](img) | desc
    # OUT: 'B1 ', ' ![](img) | desc'
    split_lines = re.split(pattern=HTML_BREAK_PATTERN, string=line, maxsplit=1, flags=re.IGNORECASE)

    if len(split_lines) <= 1:
        if DEBUG_LOG_MODIFY:
            temp = line.strip("\n")
            print(f"warning: ignore unusual line, missing br-tag: \"{temp}\"", file=sys.stderr)
        return line

    # TODO: Flags are fragile. Find a better algorithmic way to replace these.
    first = True
    column_one = True

    modified_lines = []
    for segment in split_lines:
        modified_line = segment
        if first:
            first = False
        elif column_one:
            # IN: ' ![](img) | desc'
            # OUT: ' ![](new_img)'
            if re.search(r"^( )?!\[.*?]\(.+?\)[ |]?", segment, re.IGNORECASE):
                modified_line = re.sub(replacement_pattern, fr"![\1]({new_image_path})\3", segment, re.IGNORECASE)
            else:
                # ... or
                # IN: ' | desc'
                # OUT: ' ![](new_img)'
                modified_line = f" ![]({new_image_path}) {segment}"

            column_one = False

        modified_lines.append(modified_line)

    # Join the modified lines with '<br>' as separator
    # IN: 'B1 ', ' ![](new_img) | desc'
    # OUT: B1 <br> ![](new_img) | desc
    return HTML_BREAK.join(modified_lines)


class FormatMarkdown:
    """
    Expands tables with appropriate whitespace.
    Removes extraneous whitespace around bullets.
    """
    formatted: str = None

    def __init__(self, markdown_filename):
        with open(markdown_filename, "r") as fin:
            with MarkdownRenderer(normalize_whitespace=True) as renderer:
                document = Document(fin)
                self.formatted = renderer.render(document)
