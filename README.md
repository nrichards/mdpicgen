# mdpicgen

Helps keep Markdown editing fun.

Automates maintenance of Markdown files. Generates and inserts images into a specially formatted Markdown.

## Usage

```
usage: mdpicgen [-h] [--button-pattern-file BUTTON_PATTERN_FILE]
                [--md-out-file MD_OUT_FILE] [--psd-file PSD_FILE]
                [--psd-out-dir PSD_OUT_DIR] [--image-height IMAGE_HEIGHT]
                [--print-formatted] [--print-extract]
                md_file

Read Markdown and process PSD, generating images and inserting / updating into
Markdown. PSD layer names will be used as keys. They will be matched to
formatted key sequences [configurable] found in Markdown tables with first
columns labelled "Button" [also configurable]. Layers will be composited into
images according to the sequences and saved. Images will linked into Markdown
in the second column, after the "Button" column.

positional arguments:
  md_file               Input filename for the Markdown file

options:
  -h, --help            show this help message and exit
  --button-pattern-file BUTTON_PATTERN_FILE
                        Pattern filename for matching buttons (Default:
                        'qunmk2.patset')
  --md-out-file MD_OUT_FILE
                        Output filename for Input Markdown with updated image
                        links
  --psd-file PSD_FILE   Input filename for the PSD file
  --psd-out-dir PSD_OUT_DIR
                        Output directory name for composited images, will be
                        created (Default: 'out')
  --image-height IMAGE_HEIGHT
                        Scale generated images to height (Default: 48)
  --print-formatted     Print formatted Input Markdown to stdout
  --print-extract       Print extracted buttons to stdout
```

## Origin

To help keep Markdown editing fun for projects needing to add many images which are permutations of a source diagram, this tool will do the heavy lifting.

It is designed for the needs of the Qun mk2 synthesizer project's [README.md](https://github.com/raspy135/Qun-mk2) guide, originally. The guide's images are helpful visualizations which teach synthesizer control combinations. Users study these in order to activate features on the synthesizer. There are many combinations available, and many images to generate, consequently.

Updating the images and the Markdown is work which is worthy of automation.

# Features

**Before**:

|              Button               | Description |
|:---------------------------------:|-------------|
| SHIFT + SEQ PLAY + turn dial <br> | Do thing    |

**After**:

|                          Button                          | Description |
|:--------------------------------------------------------:|-------------|
| SHIFT + SEQ PLAY + turn dial <br> ![](doc/s_splay_d.png) | Do thing    |

* Extract sequences of names of button controls directly from tables in Markdown, based upon patterns from a customizable file
* Generate images for each sequence, from the layers of a customizable illustration
* Update the original Markdown, and add missing or update outdated image links

# How to use

**Workflow**

1. Add a table with `"Button"` header text ([customizable](#button-pattern-file)) as the first column of a Markdown source document
2. Add button command sequence text, matching the format of the pattern file in use, to a cell in that table's `"Button"` column
3. Add a `<br>` tag at end of that text, inside the first cell, to mark this button sequence for processing. Repeat as desired.
4. Run the tool to generate images, and also a new Markdown file

## Details

* Tables **MUST** have a first column header name of "`Button`" ([customizable](#button-pattern-file) in `*.patset` file). Non-matching tables will be ignored.
* Each first-column cell's contents **MUST** be formatted according to the following. Non-matching cells will be ignored. `Button sequence string` `<br>` `![](optional-link-to-image)` - see an [example](#Example) below.
  * Note that the `<br>` tag is required. 
  * Note also that the image link is optional. It will be added automatically when there is a properly formatted button sequence and `<br>` tag.
* Group names of controls in a **button sequence string**, a formatted sequence. E.g. "SHIFT + B1". The separators between elements in the grouped sequences are customizable in the [patset file](#button-pattern-file).
  * Internally, the **button sequence string** is parsed to individual button names, e.g. "SHIFT" and "B1"
  * The individual button names are used to extract layers. Then a final image is composited from those layers.
* Button names may differ from the names used for the diagram layers. So, a mapping between the user-facing formatted sequence naming and the layers is implemented.
* Images are sized down to fit in tables. Use the `--image-height` parameter to customize the height.
* PSD file must have a layer titled, `"BG"`. This will be composited behind all other layers during image generation.
* PSD file layer names must include short-names. These short-names must be located after a hyphen (-) in the layer name.
  * E.g. the `"s"` in the layer name, `"SHIFT - s"`
  * See also the [image name discussion](#generated-image-names).

## Generated image names

Images are named according to their button sequence, with shortened button names.

* Names are shortened
  * E.g. "SHIFT" becomes "s", "B1" and "B2" become just `"1"` and `"2"`
* Sequence of names are concatenated together, with underscores separating the buttons that aren't the number-buttons
  * E.g. "SHIFT+B1+B2" becomes filename `"s_12.png"`

## Button pattern file

Button pattern files (`*.patset`) are used to define the matching pattern and the corresponding button's shortened name. 

The files are similar to CSV's. They are formatted and line-oriented:

| Format                | Description                                                                                                                                                                                                                                                                                                                                      |
|-----------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `^[B]?1$ = 1`         | Button patterns.<br><br>**FORMAT**: [RegEx to match buttons, as written in Markdown] = [Shortened name used to build image filenames]<br>Keys and values separated by an equals (=). <br>Keys are [regular expressions](https://docs.python.org/3/library/re.html). <br>Values are short strings used for [image names](#generated-image-names). |
| `# this is a comment` | (Optional) hash-tag (#) comment lines                                                                                                                                                                                                                                                                                                            |
| `__header__`          | An unquoted string, used to identify which tables to parse by matching against a table's first column's header text contents.                                                                                                                                                                                                                    |
| `__separator__`       | One or more quoted strings. Used help break-down, to split up a long button sequence into individual buttons. These individual buttons are then matched against the button patterns, above.                                                                                                                                                      |

A [default button pattern file](qunmk2.patset) is provided for the Qun mk2 synthesizer.

# Examples

## Markdown sample: 

1. Notice the first row's header is `Button`. This matches the default [patset file](qunmk2.patset).
2. Notice the `<br>` tag is used only once
   1. With `--md-out-file`, an image link will be added, if missing.
   2. Or it will be updated, if already in the doc.
3. Notice the "B1", "SHIFT", etc are configured in the [patset file](qunmk2.patset).


```markdown
|               Button               | Description                            |
|:----------------------------------:|----------------------------------------|
| B1 + B2 <br> ![](./doc/sample.png) | A button sequence and image            |
|          SHIFT + B3 <br>           | No image. Will be injected with image. |
|             SYS + B4               | No br-tag. Won't receive image.        |
```

## At command line -- show program options, verbosely

* `python3 __main__.py`, or `python3 __main__.py -h`

## Generate images for a Markdown file to the `out` directory

* `python3 __main__.py test.md --psd-out-dir out --psd-file test.psd`

## Add and update image links with a custom path to a new Markdown file

* `python3 __main.py__ test.md --psd-out-dir custom/image/path --md-out-file out_test_md.md`

## Print all found button sequences from a Markdown file

* `python3 __main__.py test.md --print-extract`

## Read a custom button pattern file, and find button sequences in a Markdown file

* `python3 __main__.py test.md --print-extract --button-pattern-file custom.patset`

## Utility to format and print a Markdown file

* `python3 __main__.py test.md --print-formatted`

# Limitations

* Only one `<br>` tag should be present in a cell for a matching table's first-column. With `--md-out-file`, each br-tag will result in a new image added to the Markdown.

# Requirements

* python 3.10+
* psd-tools 1.9

# Development notes

"Not fun" bits, which I plan to work on:

* Working with Photoshop PSD files is proving problematic due to compatibility issues. Everyone involved in the project does not own a license from Adobe and instead uses their own PSD editor. Also, the Python libraries to extract PSD data have their own issues, following Adobe's out-of-date and wrong specification, plus they are maintained by volunteers who may not have motivation to solve my particular compatibility issues. 
* Solution will be to migrate to 100% Python compositing. Ideas include:
  * JSON file dictating layout of named button controls
  * Layout could specify shapes and colors, e.g. "rectangle" and "orange". Shape drawing commands could then render the stylized shapes, and save the final image.
  * Or, layout could use pre-built images, and specify location, image-name, and orientation. Drawing commands could render the component images by placement, and then save the final image.
