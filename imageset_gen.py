import csv
import sys

from PIL import Image

from constants import BG_LAYER_NAME, SHORT_NAME_INFIX_SEPARATOR
from util import make_out_dir, size_from_height, ImageOpt
from button_sequence import ButtonSequence

DEBUG_LOG_IMAGESET = True
ENABLE_RESIZE = True
USE_THREADING_EXPERIMENTAL = False  # Causes truncated image rendering, buggy


class ImageSet:
    layers = {str: {}}

    def process_imageset(self, out_dirname, imageset_filename, imageset_dir, button_sequences, opt: ImageOpt):
        self.layers = self.load_imageset(imageset_filename, imageset_dir)

        make_out_dir(out_dirname)

        # Avoid redundant image generation
        processed_basenames = set()
        for sequence in button_sequences:
            basename = sequence.basename
            
            if basename not in processed_basenames:
                self.process_image(out_dirname, sequence, opt)
                processed_basenames.add(basename)
    
        print(f"composited {len(processed_basenames)} images")

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

    def process_image(self, out_dirname, sequence, opt: ImageOpt):
       
        
        
        # TODO: Group sequence of digit layers from same sequence together
        # TODO: Extend duration of button press for sequences marked "Long press". (Return duration list along with images.)
        # TODO: Flash On-Off-On for repeat patterns in a sequence


        basename = sequence.basename
        image_filename = f"{out_dirname}/{basename}.{opt.extension()}"

        if opt.gif:
            images = self.gen_animated_images(sequence, opt)

            # Save GIF, hold duration at end
            images[0].save(image_filename, save_all=True, append_images=images[1:], loop=0,
                           duration=[400] * (len(images) - 1) + [2000])
        else:
            # PNG
            layer_names: [] = self.process_basename(basename)
            composite_image = self.gen_composite_image(opt, layer_names, self.layers)
            composite_image.save(image_filename, format=opt.extension().upper())

    @staticmethod
    def process_basename(basename) -> [str]:
        compound_layer_names = basename.split(SHORT_NAME_INFIX_SEPARATOR)

        # Unpack the compound all-digit multi-character layer names to single-digit names, because they're packed
        # together for presentation purposes in the filename.
        # Keep the alphabetic strings whole, because multi-character alphabetic layer names are valid.
        layer_names = [layer_name for packed in compound_layer_names
                       for layer_name in (packed if packed.isdigit() else [packed])]

        # Always render the background layer.
        results = [BG_LAYER_NAME] + list(layer_names)

        if DEBUG_LOG_IMAGESET:
            print(f"computed layer names: {results}", file=sys.stderr)

        return results

    def gen_animated_images(self, sequence:ButtonSequence, opt):
        images = []
        composited_image = None
        
        # TODO: Sub-composite in order to simultaneously render multiple layers then remove them
        
        layer_names: [] = self.process_basename(sequence.basename)
        image_layers = [self.layers[layer_name] for layer_name in layer_names]

        for layer in image_layers:
            composited_image = self.composite_layer(composited_image, layer)
            resized = self.resize_image(opt, composited_image)
            images.append(resized)

        return images

    @staticmethod
    def gen_composite_image(opt: ImageOpt, layer_names, imageset_layers) -> Image:
        output_image = None
        imageset_layers = [(layer_name, imageset_layers[layer_name]) for layer_name in layer_names]

        for layer_name, layer in imageset_layers:
            if DEBUG_LOG_IMAGESET:
                print(f"compositing layer name '{layer_name}', layer {layer}", file=sys.stderr)

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
        return output_image.resize(size_from_height(opt.height, output_image.size)) if ENABLE_RESIZE else output_image
