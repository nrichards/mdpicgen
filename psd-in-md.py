from psd_tools import PSDImage
import os

out_dirname = 'out'
if not os.path.exists(out_dirname):
    os.mkdir(out_dirname)

psd = PSDImage.open('test.psd')

layer_names = ['SHIFT - s', 'DIAL - d', 'B5 - 5']
# layer_names = ['B5 - 5']


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

# TODO crop to desired size


image = psd.composite(
    layer_filter=lambda layer: match_layer(layer))
image.save(f'{out_dirname}/test.png')

# for layer in psd:
#     print(layer)
#     if layer.name != '':
#         layer_image = layer.composite()
#         layer_image.save('out/%s.png' % layer.name)
