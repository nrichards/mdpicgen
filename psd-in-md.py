from psd_tools import PSDImage
import os

# Renders images sized to the bounding box of this layer
BG_LAYER_NAME: str = "BG"

# Names of layers to extract
# NOTE: Trailing words in the layers are used to compose the resultant filename
layer_names: [str] = ['SHIFT - s', 'SEQ PLAY - splay', 'DIAL - d']

full_layer_names: [str] = layer_names + [BG_LAYER_NAME]

bbox = None

"BG"
"LOOPER STOP - ls"
"LOOPER PLAY - lplay"
"LOOPER REC - lr"
"PARAM - param"
"SYSTEM - sys"
"MODE PLAY - mplay"
"SEQ PLAY - splay"
"B8 - 8"
"B7 - 7"
"B6 - 6"
"B5 - 5"
"B4 - 4"
"B3 - 3"
"B2 - 2"
"B1 - 1"
"NO - n"
"OK - o"
"SHIFT - s"
"DIAL - d"

out_dirname = 'out'


def make_out_dir():
    if not os.path.exists(out_dirname):
        os.mkdir(out_dirname)


def layer_name_from_text(button_name):
    # TODO build a dictionary mapping words used in the Qun manual to layer names
    pass


def match_layer(layer, match_names):
    print(f'inspecting \"{layer.name}\"')
    if layer.name:
        if layer.name in match_names:
            print(f'matched {layer.name}, {layer.bbox}')
            return True
        elif layer.parent is not None and layer.parent.kind == 'group' and layer.parent.name in match_names:
            return True
    elif layer.parent.kind == 'group' and layer.parent.name in match_names:
        print(f'matched {layer.name}, {layer.bbox}')
        return True
    else:
        return match_layer(layer.parent, match_names)
        # False
    # elif match_layer(layer.parent, match_names):
    #     return True
    return False


def find_bbox():
    global bbox
    for layer in psd.descendants():
        print(layer)
        if BG_LAYER_NAME == layer.name:
            bbox = layer.bbox
            break
    if bbox is None:
        print(f"Warning: Bounding box layer {BG_LAYER_NAME} not found. Output images will be full size.")
        bbox = psd.bbox


def gen_image_name(names):
    image_name = ''

    for name in names:
        words = name.split()
        chunk = words[-1].strip()
        print(f'chunk {chunk}')
        if image_name != '':
            image_name += "_"
        image_name += chunk

    return image_name


make_out_dir()

psd = PSDImage.open('test.psd')

find_bbox()

image = psd.composite(
    viewport=bbox,
    layer_filter=lambda candidate_layer: match_layer(candidate_layer, full_layer_names))

new_height = 48
reduction_scalar = new_height / image.size[1]
new_width = int(reduction_scalar * image.size[0])
resized_image = image.resize([new_width, new_height])

resized_image.save(f'{out_dirname}/{gen_image_name(layer_names)}.png')

# for layer in psd:
#     print(layer)
#     if layer.name != '':
#         layer_image = layer.composite()
#         layer_image.save('out/%s.png' % layer.name)
