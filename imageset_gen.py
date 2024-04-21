import concurrent.futures
import csv
import os
import sys

from PIL import Image

from constants import BG_LAYER_NAME, SHORT_NAME_INFIX_SEPARATOR, THREADS_PER_CPU
from util import make_out_dir, size_from_height, ImageOpt

DEBUG_LOG_IMAGESET = True
ENABLE_RESIZE = True
USE_THREADING_EXPERIMENTAL = False  # Causes truncated image rendering, buggy


class ImageSet:
    layers = {str: {}}

    def process_imageset(self, out_dirname, imageset_filename, imageset_dir, basenames, opt: ImageOpt):
        self.layers = self.load_imageset(imageset_filename, imageset_dir)

        make_out_dir(out_dirname)

        # Avoid redundant image generation
        unique_basenames = list(set(basenames))
        if DEBUG_LOG_IMAGESET:
            print(f"unique_basenames: {unique_basenames}", file=sys.stderr)

        thread_count = 1
        if USE_THREADING_EXPERIMENTAL:
            thread_count = int(os.cpu_count() * THREADS_PER_CPU)

        pool = concurrent.futures.ThreadPoolExecutor(max_workers=thread_count)

        for basename in unique_basenames:
            pool.submit(self.process_image, basename, opt, out_dirname)

        pool.shutdown(wait=True)

        if DEBUG_LOG_IMAGESET:
            print(f"composited: {len(unique_basenames)}", file=sys.stderr)

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

    def process_image(self, basename, opt: ImageOpt, out_dirname):
        components = self.process_basename(basename)

        if opt.gif:
            images = []
            # images = self.gen_anim_images(opt, components, self.layers)
            # ['BG', '1', '2', '3']
            # images = images + composite( 'BG' )
            # images = images + composite( images[-1], '1' )
            # images = images + composite( images[-1], '2' )
            # images = images + composite( images[-1], '3' )
            images[0].save
            pass
        else:
            composite_image = self.gen_composite_image(opt, components, self.layers)
            composite_image.save(f"{out_dirname}/{basename}.{opt.extension()}", format=opt.extension().upper())

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

    # @staticmethod
    # def gen_anim_images(opt: ImageOpt, components, imageset_layers) -> [Image]:
    #     # Make the background image, keep a copy of it, resize it and store that into images
    #     # Make the next image by compositing with the prior, resize
    #     new_size = size_from_height(opt.height, output_image.size)
    #     if ENABLE_RESIZE:
    #         result = output_image.resize(new_size)
    #     else:
    #         result = output_image
    #
    #     images = []
    #     for component in components:
    #         layer = imageset_layers[component]
    #         if DEBUG_LOG_IMAGESET:
    #             print(f"collecting layer {component}, layer {layer}", file=sys.stderr)
    #
    #
    #         if not output_image:
    #             output_image = layer["image"].copy()
    #         else:
    #             output_image.alpha_composite(layer["image"], (layer["x"], layer["y"]))
    #
    #     new_size = size_from_height(opt.height, output_image.size)
    #     if ENABLE_RESIZE:
    #         result = output_image.resize(new_size)
    #     else:
    #         result = output_image
    #     return result

    @staticmethod
    def gen_composite_image(opt: ImageOpt, components, imageset_layers) -> Image:
        output_image = None
        for component in components:
            layer = imageset_layers[component]
            if DEBUG_LOG_IMAGESET:
                print(f"compositing layer {component}, layer {layer}", file=sys.stderr)

            if not output_image:
                output_image = layer["image"].copy()
            else:
                output_image.alpha_composite(layer["image"], (layer["x"], layer["y"]))

        new_size = size_from_height(opt.height, output_image.size)
        if ENABLE_RESIZE:
            result = output_image.resize(new_size)
        else:
            result = output_image
        return result
