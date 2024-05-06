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
    """Create a Markdown file collecting just the button sequences, grouped and sub-grouped.

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
        with MarkdownRenderer() as renderer:
            ButtonSequence.init_description(button_sequences, renderer)
            print(button_sequences)

            # TODO Derive category from description text, mapping keywords to known categories, using the best match
            # TODO Create columns 
            # TODO Create tables

            # text = Path("test_seqs.md").read_text()
            # doc = mistletoe.Document(text)
            # print_markdown_tree(doc.children)
            # print("rendering ...")
            # md = renderer.render(doc)
            # print(md)

            # #####
            # print("next ...")

            doc = mistletoe.Document("")


            # TODO Order in selection priority
            categories = {
                'Control': [],
                'Device': ['sleep', 'reset', 'board'],
                'Edit': ['copy', 'paste', 'undo', 'clear', 'change'],
                'Info': ['show', 'scroll'],
                'Load': ['load'],
                'Looper': ['looper'],
                'MIDI and presets': ['midi'],
                'Mode': ['mode', 'status page'],
                'Mute': ['mute'],
                'Navigate': ['select', 'scene', 'navigate', 'previous', 'next'],
                'Note performance': [],
                'Perform': ['playing'],
                'Performance: Run multiple sequence patterns at the same time': [],
                'Record': ['recording'],
                'Rewind': ['rewind'],
                'Save': ['save'],
                'Scratch': ['scratch', 'record'],
                'Sequencer': ['sequencer'],  # Sequencer performance
                'Sound signal performance': [],
                'Sub-mode': ['sub-mode', 'parameters'],
            }

            def print_prior_table_contents():
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
            
            def print_next_section_title(title) -> str:
                doc.children.extend(create_title_list(title))
                return title

            last_table_title = ""
            for seq in button_sequences:
                if last_table_title is not seq.section:
                    print_prior_table_contents()
                    
                    last_table_title = print_next_section_title(seq.section)
                    
                # Process a sequence
                
                # TODO Build a list of categories
                # TODO Decide on a category for each line
                # TODO Dump all the categories at once, zipping them together

            # Last table
            print_prior_table_contents()


            print("rendering ...")
            md = renderer.render(doc)
            fout.write(md)


def create_title_list(text, line_number=1):
    return [create_blankline(line_number), create_paragraph(text, line_number), create_blankline()]


def create_table(table_text):
    table = Table((table_text, 1))
    # TRICKY: line_number is required and is not set in the constructor, only in block_token.tokenize()
    table.line_number = 1
    return table


def to_table_line(elements: [str], column_count=0) -> [str]:
    cc = 1
    if column_count:
        cc = column_count
    return ["|".join(elements * cc) + "\n"]


def create_paragraph(text, line_number=1) -> [Token]:
    lines = [text + " \n"]
    result = Paragraph(lines)
    # TRICKY: line_number is required and is not set in the constructor, only in block_token.tokenize()
    result.line_number = line_number
    return result


def create_blankline(line_number=1):
    result = BlankLine([""])
    # TRICKY: line_number is required and is not set in the constructor, only in block_token.tokenize()
    result.line_number = line_number
    return result


def create_cell(text: str, line_number=1) -> [TableCell]:
    lines = [text + " \n"]
    result = TableCell(lines)
    # TRICKY: line_number is required and is not set in the constructor, only in block_token.tokenize()
    result.line_number = line_number
    return result


def create_row(row_text, line_number=1) -> TableRow:
    result = TableRow(row_text)
    # TRICKY: line_number is required and is not set in the constructor, only in block_token.tokenize()
    result.line_number = line_number
    return result



    ## System control
    # Device
    # Mode
    # Sub-mode
    # Sequencer
    # Looper
    ## Performance
    # MIDI and presets
    # Sound signal performance
    # Note performance
    ## Session and Looper data
    # Info
    # Load
    # Save
    ## Sequencer
    # Control
    # Performance
    # Edit
    ## Play Mode: SEQ CFG sub-mode
    # Performance: Run multiple sequence patterns at the same time
    ## Looper
    # Navigation
    # Performance
    # Edit
    ## Sequencer Parameter Locking
    # Navigation
    # Edit
    ## Granular
    # Edit
    # Navigate
    # Record
    # Load
    ## Vinyl Record Scratch
    # Scratch
    # Rewind
    # Mute
