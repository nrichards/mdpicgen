# Shared constants

HTML_BREAK_PATTERN = r"<br/?>"
HTML_BREAK = "<br>"

# TODO save to user-editable file for customizability
# Renders images sized to the bounding box of this layer
BG_LAYER_NAME: str = "BG"

PNG_IMAGE_EXTENSION = "png"
GIF_IMAGE_EXTENSION = "gif"

# For generating image filenames, the separator between alphanumeric chars, e.g. "s_mplay_123"
SHORT_NAME_INFIX_SEPARATOR = "_"

THREADS_PER_CPU = 0.8

# For reading the pattern text files
COMMENT_KEY = "#"
SEPARATOR_VALUE_WRAPPER = "\""  # just a quote, for later stripping of the quoted string values
SEPARATOR_KEY = "__separator__"
TABLE_HEADER_KEY = "__header__"
PATTERN_FILE_DELIMITER = "="
