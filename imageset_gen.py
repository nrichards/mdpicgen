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
        components: [] = self.process_basename(basename)
        image_filename = f"{out_dirname}/{basename}.{opt.extension()}"

        if opt.gif:
            images = self.gen_animated_images(components, opt)

            # Save GIF, hold duration at end
            images[0].save(image_filename, save_all=True, append_images=images[1:], loop=0,
                           duration=[400] * (len(images) - 1) + [2000])
        else:
            composite_image = self.gen_composite_image(opt, components, self.layers)
            composite_image.save(image_filename, format=opt.extension().upper())

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

    def gen_animated_images(self, components, opt):
        images = []
        composited_image = None
        component_layers = [self.layers[component] for component in components]

        for layer in component_layers:
            composited_image = self.composite_layer(composited_image, layer)
            resized = self.resize_image(opt, composited_image)
            images.append(resized)

        return images

    @staticmethod
    def gen_composite_image(opt: ImageOpt, components, imageset_layers) -> Image:
        output_image = None
        for component in components:
            layer = imageset_layers[component]
            if DEBUG_LOG_IMAGESET:
                print(f"compositing layer {component}, layer {layer}", file=sys.stderr)

            output_image = ImageSet.composite_layer(output_image, layer)

        result = ImageSet.resize_image(opt, output_image)
        return result

    @staticmethod
    def composite_layer(composite_image, layer) -> Image:
        if not composite_image:
            composite_image = layer["image"].copy()
        else:
            composite_image.alpha_composite(layer["image"], (layer["x"], layer["y"]))

        return composite_image

    @staticmethod
    def resize_image(opt, output_image):
        new_size = size_from_height(opt.height, output_image.size)
        if ENABLE_RESIZE:
            result = output_image.resize(new_size)
        else:
            result = output_image
        return result
