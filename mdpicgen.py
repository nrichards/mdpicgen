from extract_md import extract_button_sequences
from util import format_image_basename
from button_sequence import ButtonSequence
from modify_md import format_markdown, write_markdown
from imageset_gen import ImageSet, ImageOpt
from psd_gen import PSDInMd
from write_seqs_md import write_seqs_markdown

# noinspection PyUnresolvedReferences
mdpicgen_ignore = (extract_button_sequences, format_image_basename, ButtonSequence, format_markdown, write_markdown,
                   write_seqs_markdown)


def process_psd(out_dirname, psd_filename, basenames, height):
    PSDInMd().process_psd(out_dirname, psd_filename, basenames, height)


def process_imageset(out_dirname, imageset_filename, imageset_dir, button_sequences, opt: ImageOpt):
    ImageSet().process_imageset(out_dirname, imageset_filename, imageset_dir, button_sequences, opt)
