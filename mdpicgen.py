import csv

from PIL import Image

# noinspection PyUnresolvedReferences
from extract_md import extract_button_sequences, format_image_basename, SHORT_NAME_INFIX_SEPARATOR, ButtonSequence
# noinspection PyUnresolvedReferences
from modify_md import format_markdown, write_markdown
from psdinmd import PSDInMd


def process_psd(out_dirname, psd_filename, basenames, height):
    PSDInMd().process_psd(out_dirname, psd_filename, basenames, height)


def process_imageset(out_dirname, imageset_filename, imageset_dir, basenames, height):
    ImageSet().process_imageset(out_dirname, imageset_filename, imageset_dir, basenames, height)


class ImageSet:
    layers = []

    def process_imageset(self, out_dirname, imageset_filename, imageset_dir, basenames, height):
        self.load_imageset(imageset_filename, imageset_dir)
        print("what is next")

    def load_imageset(self, csv_file, imageset_dir):
        with open(csv_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                layer = {
                    "image": self.load_image(f"{imageset_dir}/{row['image_file']}"),
                    "layer_name": row['layer_name'],
                    "x": int(row['x_pos']),
                    "y": int(row['y_pos']),
                }
                self.layers.append(layer)

        # TODO do something with the layer
        print(self.layers)

    def load_image(self, image_filename):
        return Image.open(image_filename)
