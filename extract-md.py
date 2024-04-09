# TODO
# Extract the potential button combos from a markdown file, e.g.
# `MODE PLAY + SYSTEM + turn dial | ![](./manual_images/but/mplay_sys_d.png) | Looper master volume`
# `SYSTEM + turn dial | ![](./manual_images/but/sys_d.png) | VCF volume`
# Yields
# ["MODE PLAY + SYSTEM + turn dial", "SYSTEM + turn dial"]

# TODO
# Keep line-number of finding
# E.g. {284 : "MODE PLAY + SYSTEM + turn dial", 285: "SYSTEM + turn dial"}


# TODO handle case where button combo starts at 3rd column
# `Stop | Stop      | LOOPER REC + LOOPER PLAY | ![](./manual_images/but/lr_lplay.png) | Looper stand-by`
# OR simply rewrite the Markdown to always have the buttons in the 1st column