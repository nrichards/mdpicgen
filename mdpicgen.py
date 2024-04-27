from extract_md import extract_button_sequences, format_image_basename, ButtonSequence
from modify_md import format_markdown, write_markdown
from imageset_gen import ImageSet, ImageOpt
from psd_gen import PSDInMd

# noinspection PyUnresolvedReferences
mdpicgen_ignore = extract_button_sequences, format_image_basename, ButtonSequence, format_markdown, write_markdown


def process_psd(out_dirname, psd_filename, basenames, height):
    PSDInMd().process_psd(out_dirname, psd_filename, basenames, height)


def process_imageset(out_dirname, imageset_filename, imageset_dir, button_sequences, opt: ImageOpt):
    ImageSet().process_imageset(out_dirname, imageset_filename, imageset_dir, button_sequences, opt)
