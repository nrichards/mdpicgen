import concurrent.futures
import os
import sys

from psd_tools import PSDImage

# noinspection PyUnresolvedReferences
from extract_md import extract_button_sequences, format_image_basename, SHORT_NAME_INFIX_SEPARATOR, ButtonSequence
# noinspection PyUnresolvedReferences
from modify_md import format_markdown, write_markdown

# For debugging generating
DEBUG_LOG_IMAGE = True

# TODO extract to .. someplace, for customizability
# Renders images sized to the bounding box of this layer
BG_LAYER_NAME: str = "BG"


def make_out_dir(out_dirname):
    if not os.path.exists(out_dirname):
        os.mkdir(out_dirname)


def process_psd(out_dirname, psd_filename, basenames, height):
    PSDInMd().process_psd(out_dirname, psd_filename, basenames, height)


class PSDInMd:
    bbox = None
    psd = None

    def can_find_layer_for_any_shortname(self, layer, match_components) -> bool:
        """
        Breaks shortnames into small chunks, "components".
        Searches the PSD structure to determine if the current layer should be composited: when it matches
         one of the components.
        """
        if DEBUG_LOG_IMAGE:
            print(f'inspecting \"{layer.name}\"', file=sys.stderr)

        # Optimization: collect the shortname which this layer represents.
        # The PSD has been designed to have shortnames embedded in its layer names.
        # They are located after a hyphen (-) in the layer name.
        layer_component_name = None
        if layer.name:
            layer_component_name = layer.name.split('-')[-1].strip()
        layer_parent_component_name = None
        if layer.parent and layer.parent.name:
            layer_parent_component_name = layer.parent.name.split('-')[-1].strip()

        # Search through the PSD for the appropriate layer that matches any of component we're interested in
        if layer.name:
            if layer_component_name in match_components:
                if DEBUG_LOG_IMAGE:
                    print(f'matched {layer_component_name}, {layer.bbox}', file=sys.stderr)
                return True
            elif layer.parent and layer.parent.kind == 'group' and layer_parent_component_name in match_components:
                return True
        elif layer.parent.kind == 'group' and layer_parent_component_name in match_components:
            if DEBUG_LOG_IMAGE:
                print(f'matched {layer_parent_component_name}, {layer.parent.bbox}', file=sys.stderr)
            return True
        else:
            # TRICKY: Recursion
            return self.can_find_layer_for_any_shortname(layer.parent, match_components)

        return False

    def find_bbox(self):
        global bbox
        for layer in self.psd.descendants():
            if DEBUG_LOG_IMAGE:
                print(layer)
            if BG_LAYER_NAME == layer.name:
                bbox = layer.bbox
                break
        if bbox is None:
            print(f"Warning: Bounding box layer {BG_LAYER_NAME} not found. Output images will be full size.")
            bbox = self.psd.bbox

    def process_psd(self, out_dirname, psd_filename, basenames, height):
        """
        Writes image files named using the basenames and placed in the out_dirname.
        Images are composited from the PSD file according to substrings of the basenames, called "components".
        PSD has named layers, and the basenames are formatted to reference the layer names.
        Break the basenames apart (into "components") then search for matching layers, then composite that all into an
        image.
        """
        make_out_dir(out_dirname)

        self.psd = PSDImage.open(psd_filename)
        self.find_bbox()

        # Avoid redundant image generation. Uniquify the list of basenames.
        unique_basenames = list(set(basenames))

        # Performance metrics for posterity: 10-core, MacBook Pro, 16-inch, 2021, Apple M1 Pro, 16GB, Sonoma 14.4.1
        #   2: python3 ../psd-in-md README.md --md-out-file foopy.md --psd-file     198.15s user 90.12s system 189% cpu 2:31.85 total
        #   5: python3 ../psd-in-md README.md --md-out-file foopy.md --psd-file     227.42s user 120.66s system 407% cpu 1:25.39 total
        #   6: python3 ../psd-in-md README.md --md-out-file foopy.md --psd-file     235.32s user 132.78s system 448% cpu 1:22.04 total
        #   8: python3 ../psd-in-md README.md --md-out-file foopy.md --psd-file     248.46s user 151.97s system 505% cpu 1:19.18 total
        #   10: python3 ../psd-in-md README.md --md-out-file foopy.md --psd-file     259.84s user 162.87s system 530% cpu 1:19.63 total
        #   12: python3 ../psd-in-md README.md --md-out-file foopy.md --psd-file     256.55s user 193.13s system 418% cpu 1:47.42 total
        #   20: python3 ../psd-in-md README.md --md-out-file foopy.md --psd-file     261.15s user 347.56s system 389% cpu 2:36.09 total
        decent_performance = int(os.cpu_count() * 0.8)
        if DEBUG_LOG_IMAGE:
            print(f"thread count: {decent_performance}", file=sys.stderr)

        pool = concurrent.futures.ThreadPoolExecutor(max_workers=decent_performance)

        for basename in unique_basenames:
            pool.submit(self.composite_image, basename, height, out_dirname)

        pool.shutdown(wait=True)

    def composite_image(self, basename, height, out_dirname):
        # Prepare the component names to be matched with layers.
        #  - Remove separators, and separate digits.
        # E.g. 'lplay_12345' -> ['lplay', '1', '2', '3', '4', '5']
        components = basename.split(SHORT_NAME_INFIX_SEPARATOR)

        temp = []
        for component in components:
            if component.isdigit():
                temp = temp + [*component]
            else:
                temp = temp + [component]
        components = temp

        # Always render the background layer.
        components = components + [BG_LAYER_NAME]
        image = self.psd.composite(
            viewport=bbox,
            layer_filter=lambda candidate_layer: self.can_find_layer_for_any_shortname(candidate_layer, components))

        new_height = height
        reduction_scalar = new_height / image.size[1]
        new_width = int(reduction_scalar * image.size[0])
        resized_image = image.resize([new_width, new_height])

        resized_image.save(f'{out_dirname}/{basename}.png')
