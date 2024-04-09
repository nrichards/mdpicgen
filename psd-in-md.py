from psd_tools import PSDImage
import os

# Renders images sized to the bounding box of this layer
BG_LAYER_NAME: str = "BG"

# Names of layers to extract
# NOTE: Trailing words in the layers are used to compose the resultant filename
layer_names: [str] = ['SHIFT - s', 'SEQ PLAY - splay', 'DIAL - d']

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


def make_out():
    if not os.path.exists(out_dirname):
        os.mkdir(out_dirname)


def layer_name_from(button_name):
    # TODO build a dictionary mapping words used in the Qun manual to layer names
    pass


psd = PSDImage.open('test.psd')


def match_layer(layer, names):
    print(f'{layer.name}')
    if layer.name:
        if layer.name in layer_names:
            # print(f'matched, {layer.bbox}')
            return True
    elif layer.parent.kind == 'group' and layer.parent.name in layer_names:
        # print(f'matched, {layer.bbox}')
        return True
    return False


bbox = None


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


find_bbox()


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


full_layer_names: [str] = layer_names + [BG_LAYER_NAME]

image = psd.composite(
    viewport=bbox,
    layer_filter=lambda candidate_layer: match_layer(candidate_layer, full_layer_names))

image.save(f'{out_dirname}/{gen_image_name(layer_names)}.png')

print(image.getbbox())

# for layer in psd:
#     print(layer)
#     if layer.name != '':
#         layer_image = layer.composite()
#         layer_image.save('out/%s.png' % layer.name)
