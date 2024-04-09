from psd_tools import PSDImage
import os

out_dirname = 'out'
if  not os.path.exists(out_dirname):
    os.mkdir(out_dirname)

psd = PSDImage.open('test.psd')

layer_names = ['SHIFT - s', 'DIAL - d', 'B5 - 5']

image = psd.composite(
    layer_filter=lambda layer: layer.is_visible() and layer.name in layer_names)
image.save(f'{out_dirname}/test.png')
#
# for layer in psd:
#     print(layer)
#     if layer.name != '':
#         layer_image = layer.composite()
#         layer_image.save('out/%s.png' % layer.name)
