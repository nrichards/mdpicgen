from psd_tools import PSDImage
import os
import sys

# noinspection PyUnresolvedReferences
from modify_md import format_markdown
# noinspection PyUnresolvedReferences
from extract_md import extract_buttons, format_image_basename, SHORT_NAME_INFIX_SEPARATOR

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

        # Search through the PSD for a
        if layer.name:
            if layer_component_name in match_components:
                print(f'matched {layer_component_name}, {layer.bbox}', file=sys.stderr)
                return True
            elif layer.parent and layer.parent.kind == 'group' and layer_parent_component_name in match_components:
                return True
        elif layer.parent.kind == 'group' and layer_parent_component_name in match_components:
            print(f'matched {layer_parent_component_name}, {layer.parent.bbox}', file=sys.stderr)
            return True
        else:
            # TRICKY: Recursion
            return self.can_find_layer_for_any_shortname(layer.parent, match_components)

        return False

    def find_bbox(self):
        global bbox
        for layer in self.psd.descendants():
            print(layer)
            if BG_LAYER_NAME == layer.name:
                bbox = layer.bbox
                break
        if bbox is None:
            print(f"Warning: Bounding box layer {BG_LAYER_NAME} not found. Output images will be full size.")
            bbox = self.psd.bbox

    def process_psd(self, out_dirname, psd_filename, basenames, height):
        make_out_dir(out_dirname)

        self.psd = PSDImage.open(psd_filename)
        self.find_bbox()

        # Avoid redundant image generation. Uniquify the list of basenames.
        unique_basenames = list(set(basenames))

        for basename in unique_basenames:
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
