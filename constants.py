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
DIGITS_MACRO_NAME = "%digits%"

# For reading the imageset CSV text files - (single-quoted for string interpolation, please)
Y_POS_CSV_HEADER = 'y_pos'
X_POS_CSV_HEADER = 'x_pos'
LAYER_NAME_CSV_HEADER = 'layer_name'
IMAGE_FILE_CSV_HEADER = 'image_file'

GIF_END_FRAME_DURATION_MS = 2000
GIF_MID_FRAME_DURATION_MS = 400
