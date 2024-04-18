import csv

# noinspection PyUnresolvedReferences
from extract_md import extract_button_sequences, format_image_basename, SHORT_NAME_INFIX_SEPARATOR, ButtonSequence
# noinspection PyUnresolvedReferences
from modify_md import format_markdown, write_markdown
from psdinmd import PSDInMd


def process_psd(out_dirname, psd_filename, basenames, height):
    PSDInMd().process_psd(out_dirname, psd_filename, basenames, height)


def process_imageset(out_dirname, imageset_filename, basenames, height):
    ims = ImageSet()
    pass


class ImageSet():
    def read_scene_description(self, csv_file):
        """
        Reads the scene description from a CSV file.

        Args:
            csv_file: Path to the CSV file containing scene information.

        Returns:
            A list of dictionaries, where each dictionary represents a layer.
        """
        layers = []
        with open(csv_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                layer = {
                    "image": self.load_image(row["image_file"]),
                    "layer_name": row["layer_name"],
                    "x": int(row["x_pos"]),
                    "y": int(row["y_pos"]),
                }
                # # Add optional values if included in the CSV
                # if "width" in row:
                #     layer["width"] = int(row["width"])
                # if "height

        # TODO do something with the layer
        pass


    def load_image(self, image_filename):
        pass
