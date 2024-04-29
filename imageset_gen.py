import csv
import sys

from PIL import Image

from constants import BG_LAYER_NAME, SHORT_NAME_INFIX_SEPARATOR, Y_POS_CSV_HEADER, X_POS_CSV_HEADER, \
    LAYER_NAME_CSV_HEADER, IMAGE_FILE_CSV_HEADER, GIF_END_FRAME_DURATION_MS, GIF_MID_FRAME_DURATION_MS
from util import make_out_dir, size_from_height, ImageOpt
from button_sequence import ButtonSequence

DEBUG_LOG_IMAGESET = True
ENABLE_RESIZE = True
USE_THREADING_EXPERIMENTAL = False  # Causes truncated image rendering, buggy


class ImageLayer:
    image: Image
    layer_name: str
    x: int
    y: int

    def __init__(self, image: Image, layer_name: str, x: int, y: int):
        self.image = image
        self.layer_name = layer_name
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return "<%s.%s layer_name=%s x=%d y=%d image=%s at 0x%X>" % (
            self.__class__.__module__,
            self.__class__.__name__,
            self.layer_name,
            self.x,
            self.y,
            self.image,
            id(self),
        )


class ImageSet:
    all_layers: {str: ImageLayer} = {}

    def process_imageset(self, out_dirname, imageset_filename, imageset_dir, button_sequences, opt: ImageOpt):
        self.all_layers = self.load_imageset(imageset_filename, imageset_dir)

        make_out_dir(out_dirname)

        # Avoid redundant image generation
        processed_basenames = set()
        for sequence in button_sequences:
            basename = sequence.basename

            if basename not in processed_basenames:
                self.process_image(out_dirname, sequence, opt)
                processed_basenames.add(basename)

        print(f"composited {len(processed_basenames)} images")

    def load_imageset(self, csv_file, imageset_dir) -> {str: ImageLayer}:
        """ Loads CSV of imageset data
        :return: Dictionary of layer names to ImageLayer objects
        """
        results = {}
        with open(csv_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                row: dict  # Workaround for https://youtrack.jetbrains.com/issue/PY-60440
                layer = ImageLayer(
                    image=self.load_image(f"{imageset_dir}/{row[IMAGE_FILE_CSV_HEADER]}"),
                    layer_name=row[LAYER_NAME_CSV_HEADER],
                    x=int(row[X_POS_CSV_HEADER]),
                    y=int(row[Y_POS_CSV_HEADER]),
                )

                results[layer.layer_name] = layer

        if DEBUG_LOG_IMAGESET:
            print(results, file=sys.stderr)

        return results

    @staticmethod
    def load_image(image_filename):
        return Image.open(image_filename)

    def process_image(self, out_dirname, sequence, opt: ImageOpt):
        basename = sequence.basename
        image_filename = f"{out_dirname}/{basename}.{opt.extension()}"

        if opt.gif:
            images, durations = self.gen_animated_images(sequence, opt)

            images[0].save(image_filename, save_all=True, append_images=images[1:], loop=0,
                           duration=durations, format=opt.extension().upper())
        else:
            # PNG
            layer_names: [] = ImageSet.layer_names_from_basename(basename=basename)

            if DEBUG_LOG_IMAGESET:
                print(f"computed layer names: {layer_names}", file=sys.stderr)

            composite_image = self.gen_composite_image(opt, layer_names, self.all_layers)
            composite_image.save(image_filename, format=opt.extension().upper())

    @staticmethod
    def layer_names_from_basename(*, basename, unpack_digits=True, add_bg=True) -> [str]:
        """Transform a formatted layered image filename to a list of names, suitable for looking up its component
         layers.

        :param basename: formatted layered image filename
        :param unpack_digits: Whether to unpack compound multi-digit names to individual digit layer names
        :param add_bg: Whether to ask for rending a background layer
        :return: List of layer names, conditionally including compound multi-digit names.
        """
        results = []
        compound_layer_names = basename.split(SHORT_NAME_INFIX_SEPARATOR)

        # Split by infix separator.
        # Keep the alphabetic strings whole, because multi-character alphabetic layer names are valid.
        # Conditionally unpack compound all-digit multi-character layer names to single-digit names.
        # Unpack because they're packed together for presentation purposes in the filename.
        layer_names = [layer_name for packed in compound_layer_names
                       for layer_name in (packed if packed.isdigit() and unpack_digits else [packed])]

        if add_bg:
            results.append(BG_LAYER_NAME)

        results.extend(layer_names)

        return results

    def gen_animated_images(self, sequence: ButtonSequence, opt) -> ([Image], [int]):
        """
        Composites images as a series of images. Defines a duration list for each frame with a hold at its end.
        
        :param sequence: 
        :param opt: 
        :return: List of images, and durations for those images.
        """
        # TODO: Extend duration of button press for sequences marked "Long press". (Return duration list along with images.)
        # TODO: Flash On-Off-On for repeat patterns in a sequence

        packed_layer_names: [] = ImageSet.layer_names_from_basename(basename=sequence.basename, unpack_digits=False)
        grouped_layer_names = [ImageSet.layer_names_from_basename(basename=name, unpack_digits=True, add_bg=False)
                               for name in packed_layer_names]

        if DEBUG_LOG_IMAGESET:
            print(f"grouped layer names: {grouped_layer_names}", file=sys.stderr)

        # composite layer groups into each new image frame
        
        grouped_images = []
        composited_image = None
        for ungrouped_layer_names in grouped_layer_names:
            ungrouped_image_layers = [self.all_layers[layer_name] for layer_name in ungrouped_layer_names]
            
            for layer in ungrouped_image_layers:
                composited_image = self.composite_layer(composited_image, layer)
            resized = ImageSet.resize_image(opt, composited_image)
            grouped_images.append(resized)

        durations = [GIF_MID_FRAME_DURATION_MS] * (len(grouped_images) - 1) + [GIF_END_FRAME_DURATION_MS]

        # return images, durations
        return grouped_images, durations

    @staticmethod
    def gen_composite_image(opt: ImageOpt, layer_names, layers: {str: ImageLayer}) -> Image:
        working_image = None
        layers = [(layer_name, layers[layer_name]) for layer_name in layer_names]

        for layer_name, layer in layers:
            if DEBUG_LOG_IMAGESET:
                print(f"compositing layer name '{layer_name}', layer {layer}", file=sys.stderr)

            working_image = ImageSet.composite_layer(working_image, layer)

        result = ImageSet.resize_image(opt, working_image)
        return result

    @staticmethod
    def composite_layer(composite_image, layer: ImageLayer) -> Image:
        if not composite_image:
            composite_image = layer.image.copy()
        else:
            composite_image.alpha_composite(layer.image, (layer.x, layer.y))

        return composite_image

    @staticmethod
    def resize_image(opt, output_image):
        return output_image.resize(size_from_height(opt.height, output_image.size)) if ENABLE_RESIZE else output_image
