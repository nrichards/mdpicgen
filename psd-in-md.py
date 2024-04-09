from psd_tools import PSDImage
import os

# Renders images sized to the bounding box of this layer
BBOX_LAYER_NAME = "BG"

layer_names = ['SHIFT - s', 'DIAL - d', 'B5 - 5']

out_dirname = 'out'
if not os.path.exists(out_dirname):
    os.mkdir(out_dirname)

psd = PSDImage.open('test.psd')


def match_layer(layer):
    print(f'examining "{layer.name}"')
    if layer.name:
        if layer.name in layer_names:
            print(f'matched, {layer.bbox}')
            return True
    elif layer.parent.kind == 'group' and layer.parent.name in layer_names:
        print(f'matched, {layer.bbox}')
        return True
    return False



bbox = None

for layer in psd.descendants():
    print(layer)
    if BBOX_LAYER_NAME == layer.name:
        bbox = layer.bbox
        break

if bbox is None:
    print(f"Warning: Bounding box layer {BBOX_LAYER_NAME} not found. Output images will be full size.")
    bbox = psd.bbox

print(f'bbox {bbox}')

image = psd.composite(
    viewport=bbox,
    layer_filter=lambda candidate_layer: match_layer(candidate_layer))
image.save(f'{out_dirname}/test.png')

print(image.getbbox())

# for layer in psd:
#     print(layer)
#     if layer.name != '':
#         layer_image = layer.composite()
#         layer_image.save('out/%s.png' % layer.name)
