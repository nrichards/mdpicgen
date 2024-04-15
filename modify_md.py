import mistletoe
from mistletoe import markdown_renderer, ast_renderer
from mistletoe.block_token import BlockToken, Heading, Paragraph, SetextHeading
from mistletoe.markdown_renderer import MarkdownRenderer
from mistletoe.span_token import InlineCode, RawText, SpanToken

from extract_md import ButtonSequence


def format_markdown(markdown_filename):
    formatter = FormatMarkdown(markdown_filename)
    return formatter.formatted


def write_markdown(md_out_file, md_in_file, button_sequences: [ButtonSequence]):
    print("write_markdown ... yeah")
    # TODO


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


##
## WORK IN PROGRESS, DO NOT USE
##

class ChangeMarkdown:
    """
    Expands tables with appropriate whitespace
    """

    def __init__(self, markdown_filename):
        with open(markdown_filename, "r") as fin:
            with MarkdownRenderer() as renderer:
                document = mistletoe.Document(fin)
                self.update_block(document)
                md = renderer.render(document)
                print(md)

    def update_text(self, token: SpanToken):
        """Update the text contents of a span token and its children.
        `InlineCode` tokens are left unchanged."""
        if isinstance(token, RawText):
            token.content = token.content.replace("mistletoe", "The Amazing mistletoe")

        if not isinstance(token, InlineCode) and hasattr(token, "children"):
            for child in token.children:
                self.update_text(child)

    def update_block(self, token: BlockToken):
        """Update the text contents of paragraphs and headings within this block,
        and recursively within its children."""
        if isinstance(token, (Paragraph, SetextHeading, Heading)):
            for child in token.children:
                self.update_text(child)

        for child in token.children:
            if isinstance(child, BlockToken):
                self.update_block(child)
