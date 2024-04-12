import mistletoe
from mistletoe import markdown_renderer, ast_renderer
from mistletoe.block_token import BlockToken, Heading, Paragraph, SetextHeading
from mistletoe.markdown_renderer import MarkdownRenderer
from mistletoe.span_token import InlineCode, RawText, SpanToken


# TODO
# Keep line-number of finding
# E.g. {284 : "MODE PLAY + SYSTEM + turn dial", 285: "SYSTEM + turn dial"}


def format_markdown(markdown_filename):
    FormatMarkdown(markdown_filename)


class FormatMarkdown:
    """
    Expands tables with appropriate whitespace.
    Removes extraneous whitespace around bullets.
    """

    def __init__(self, markdown_filename):
        with open(markdown_filename, "r") as fin:
            with MarkdownRenderer(normalize_whitespace=True) as renderer:
                document = mistletoe.Document(fin)
                md = renderer.render(document)
                print(md)


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


# TEST TODO
# TEST TODO
# TEST TODO remove me
# format_markdown("full.md")
# format_markdown("small.md")

# TEST TODO
# TEST TODO
# TEST TODO


# Extract tables

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


# Blablabla
# | Name | Age |
# |---|---|
# | Alice | 25 |
# | Bob | 30 |
# Blablabla
#
#
# Blablabla
# Name | Age
# ---|---
# Alice | 25
# Bob | 30
# Blablabla


# 1
# 1 (Long press)
#
# 2
# 2 (Long press)
# 2 in SEQ CFG sub-mode (Long press)
#
# 3
# 3 (Long press)
# 3 in SEQ CFG sub-mode (Long press)
#
# 4
# 4 (Long press)
#
# 5
# 5 (Long press)
#
# 6
# 6 (Long press)
#
# 7
# 7 (Long press)
#
# 8
#
# B 7 or 8
#
# B 7 or 8 + turn dial
#
# B[1-8]
#
# B[1-8] (Long press), then PARAM
#
# B[1-8] + NO / OK
#
# B[1-8] + PARAM + turn dial
#
# B[1-8] + turn dial
#
# Dial
#
# LOOPER PLAY
#
# LOOPER PLAY + NO or OK
#
# LOOPER PLAY + [1-5]
#
# LOOPER PLAY + [1-5] + turn dial
#
# LOOPER REC + LOOPER PLAY
#
# LOOPER STOP
#
# MODE PLAY
#
# MODE PLAY (RECALL) + B[1-8]
#
# MODE PLAY (RECALL) + B[1-8] + turn dial
#
# MODE PLAY (RECALL) + [1-8]
#
# MODE PLAY + PARAM + turn dial
#
# MODE PLAY + SYSTEM + turn dial
#
# MODE PLAY + turn dial
#
# NO
# NO (<)
#
# NO or OK button while selecting a session
#
# OK
# OK (>)
#
# PARAM
#
# PARAM (Long press)
#
# PARAM + NO
#
# PARAM + [1-3]
#
# PARAM + turn dial
#
# Press B[1-8] while booting
#
# REC
#
# REC + LOOPER PLAY
#
# REC + NO
#
# REC + OK
#
# REC + PARAM
#
# REC + SEQ PLAY
#
# REC + SEQ PLAY + turn dial
#
# REC + [1-3, 7,8]
#
# REC + turn dial
#
# SEQ PLAY
#
# SEQ PLAY + B[1-8] (Primary pattern) + B[1-8] (2nd pattern) in any sub-mode
#
# SEQ PLAY + NO / OK
#
# SEQ PLAY + [1-8]
#
# SEQ PLAY + [1-8] + turn dial
#
# SEQ PLAY + [1-8] , [1-8]...
#
# SHIFT
#
# SHIFT + Button 7
#
# SHIFT + Button 8
#
# SHIFT + LOOPER PLAY
#
# SHIFT + LOOPER PLAY + [1-3] button
#
# SHIFT + LOOPER PLAY + turn dial
#
# SHIFT + LOOPER REC
#
# SHIFT + LOOPER STOP
#
# SHIFT + Looper Stop
#
# SHIFT + MODE PLAY
#
# SHIFT + MODE PLAY + turn dial
#
# SHIFT + NO
#
# SHIFT + NO + OK
#
# SHIFT + OK
# SHIFT + OK (Before loading)
#
# SHIFT + PARAM
#
# SHIFT + REC
#
# SHIFT + REC (Long press)
#
# SHIFT + REC + B[1-3]
#
# SHIFT + SEQ PLAY +  NO / OK
#
# SHIFT + SEQ PLAY + turn dial
#
# SHIFT + SYSTEM
#
# SHIFT + turn dial <br> clockwise almost to end
#
# SYSTEM
#
# SYSTEM + PARAM + turn dial
#
# SYSTEM + [1-8]
#
# SYSTEM + turn dial
#
# Turn dial
#
# [1-8] button
