import concurrent.futures
import csv
import os
import sys

from PIL import Image

from constants import BG_LAYER_NAME, IMAGE_EXTENSION, SHORT_NAME_INFIX_SEPARATOR
from util import make_out_dir, size_from_height

DEBUG_LOG_IMAGESET = False
RESIZE_IMAGE = True
USE_THREADING_EXPERIMENTAL = False  # Causes truncated image rendering, buggy


class ImageSet:
    layers = {str: {}}

    def process_imageset(self, out_dirname, imageset_filename, imageset_dir, basenames, height):
        self.layers = self.load_imageset(imageset_filename, imageset_dir)

        make_out_dir(out_dirname)

        # Avoid redundant image generation
        unique_basenames = list(set(basenames))
        if DEBUG_LOG_IMAGESET:
            print(f"unique_basenames: {unique_basenames}", file=sys.stderr)

        thread_count = 1
        if USE_THREADING_EXPERIMENTAL:
            thread_count = int(os.cpu_count() * 0.8)

        pool = concurrent.futures.ThreadPoolExecutor(max_workers=thread_count)

        for basename in unique_basenames:
            pool.submit(self.process_image, basename, height, out_dirname)

        pool.shutdown(wait=True)

        if DEBUG_LOG_IMAGESET:
            print(f"composited: {len(unique_basenames)}", file=sys.stderr)

    def process_image(self, basename, height, out_dirname):
        components = self.process_basename(basename)
        composite_image = self.generate_image(out_dirname, height, components, self.layers)
        composite_image.save(f"{out_dirname}/{basename}.{IMAGE_EXTENSION}", format=IMAGE_EXTENSION.upper())

    @staticmethod
    def process_basename(basename) -> [str]:
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
                row: dict  # Workaround for https://youtrack.jetbrains.com/issue/PY-60440
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

    @staticmethod
    def load_image(image_filename):
        return Image.open(image_filename)

    @staticmethod
    def generate_image(out_dirname, height, components, imageset_layers) -> Image:
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
                output_image.alpha_composite(layer["image"], (layer["x"], layer["y"]))

        new_size = size_from_height(height, output_image.size)
        if RESIZE_IMAGE:
            result = output_image.resize(new_size)
        else:
            result = output_image
        return result
