import csv
import sys

from PIL import Image

from constants import BG_LAYER_NAME, IMAGE_EXTENSION
from extract_md import SHORT_NAME_INFIX_SEPARATOR
from util import make_out_dir, size_from_height

DEBUG_LOG_IMAGESET = False


class ImageSet:
    layers = {str: {}}

    def process_imageset(self, out_dirname, imageset_filename, imageset_dir, basenames, height):
        self.layers = self.load_imageset(imageset_filename, imageset_dir)

        make_out_dir(out_dirname)

        # Avoid redundant image generation
        unique_basenames = list(set(basenames))
        if DEBUG_LOG_IMAGESET:
            print(f"unique_basenames: {unique_basenames}", file=sys.stderr)

        for basename in unique_basenames:
            components = self.process_basename(basename)

            composite_image = self.generate_image(out_dirname, height, components, self.layers)
            composite_image.save(f"{out_dirname}/{basename}.{IMAGE_EXTENSION}", format=IMAGE_EXTENSION.upper())

        if DEBUG_LOG_IMAGESET:
            print(f"composited: {len(unique_basenames)}", file=sys.stderr)

    def process_basename(self, basename) -> [str]:
        intermediate_components = basename.split(SHORT_NAME_INFIX_SEPARATOR)

        components = []
        for component in intermediate_components:
            if component.isdigit():
                components = components + [*component]
            else:
                components = components + [component]

        # Always render the background layer.
        results = [BG_LAYER_NAME] + components

        if DEBUG_LOG_IMAGESET:
            print(f"components: {results}", file=sys.stderr)

        return results

    def load_imageset(self, csv_file, imageset_dir) -> {}:
        results = {}
        with open(csv_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                layer = {
                    "image": self.load_image(f"{imageset_dir}/{row['image_file']}"),
                    "layer_name": row["layer_name"],
                    "x": int(row["x_pos"]),
                    "y": int(row["y_pos"]),
                }

                results[layer["layer_name"]] = layer

        if DEBUG_LOG_IMAGESET:
            print(results, file=sys.stderr)

        return results

    def load_image(self, image_filename):
        return Image.open(image_filename)

    def generate_image(self, out_dirname, height, components, imageset_layers) -> Image:
        if DEBUG_LOG_IMAGESET:
            print(f"generating imageset to dir '{out_dirname}'", file=sys.stderr)

        output_image = None
        for component in components:
            layer = imageset_layers[component]
            if DEBUG_LOG_IMAGESET:
                print(f"compositing layer {component}, layer {layer}", file=sys.stderr)

            if not output_image:
                output_image = layer["image"].copy()
            else:
                output_image.paste(layer["image"], (layer["x"], layer["y"]))

        new_size = size_from_height(height, output_image.size)
        result = output_image.resize(new_size)
        return result
