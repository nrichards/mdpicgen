# noinspection PyUnresolvedReferences
from extract_md import extract_button_sequences, format_image_basename, ButtonSequence
# noinspection PyUnresolvedReferences
from modify_md import format_markdown, write_markdown
from imageset_gen import ImageSet
from psd_gen import PSDInMd


def process_psd(out_dirname, psd_filename, basenames, height):
    PSDInMd().process_psd(out_dirname, psd_filename, basenames, height)


def process_imageset(out_dirname, imageset_filename, imageset_dir, basenames, height):
    ImageSet().process_imageset(out_dirname, imageset_filename, imageset_dir, basenames, height)
