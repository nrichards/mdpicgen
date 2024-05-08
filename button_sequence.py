from mistletoe.block_token import TableCell
from mistletoe.markdown_renderer import MarkdownRenderer

import util
from util import format_image_basename, truncate


class ButtonSequence:
    """Button command sequence data: full text, layer names, composite filename, and origin."""
    sequence_mapping: [{}]
    line_number: int
    basename: str = ""
    section: str = ""

    description: str = ""
    """Set with set_descriptions(), below."""

    def __init__(self, *, mapping, line_no, section_title, description_tablecell: TableCell):
        self.sequence_mapping = mapping
        self.line_number = line_no
        self.section = section_title
        self.description_tablecell = description_tablecell
        self.basename = format_image_basename(self.sequence_mapping)

    def __repr__(self) -> str:
        return ("<%s.%s sequence_mapping=%s line_number=%d section='%s' desc-tokens=%d description='%s' basename='%s' "
                "at 0x%X>") % (
            self.__class__.__module__,
            self.__class__.__name__,
            self.sequence_mapping,
            self.line_number,
            truncate(self.section),
            self.description_tablecell is not None,
            truncate(self.description),
            self.basename,
            id(self),
        )

    def description_printable(self, elide: bool = False):
        result = self.description.replace('\n', ' ')
        if elide:
            result = util.truncate(result)
        return result

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

    @staticmethod
    def descriptions(button_sequences: ["ButtonSequence"], renderer: MarkdownRenderer):
        if button_sequences and type(button_sequences[0]) is not ButtonSequence:
            print(
                f"error: can't extract descriptions from sequence list, "
                f"unsupported type: {type(button_sequences[0])}")
            return

        return [renderer.render_table_cell(tablecell) for tablecell in
                [seq.description_tablecell for seq in button_sequences]]

    @staticmethod
    def init_description(button_sequences: ["ButtonSequence"], renderer: MarkdownRenderer):
        descriptions = ButtonSequence.descriptions(button_sequences, renderer)
        for seq, desc in zip(button_sequences, descriptions):
            seq.description = desc
