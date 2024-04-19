# mdpicgen

Helps keep Markdown editing fun.

Automates maintenance of Markdown files containing patterend images. Generates from, and inserts or updates images into a Markdown.

## Usage

```
usage: mdpicgen [-h] --md-file MD_FILE [--md-out-file MD_OUT_FILE]
                [--image-out-dir IMAGE_OUT_DIR]
                [--button-pattern-file BUTTON_PATTERN_FILE]
                [--image-height IMAGE_HEIGHT] [--print-formatted]
                [--print-extract]
                {imageset,psd} ...

Read Markdown and process image layers, generating images and inserting /
updating into Markdown. Layer names will be used as keys. They will be matched
to formatted key sequences [configurable] found in Markdown tables with first
columns labelled "Button" [also configurable]. Layers will be composited into
images according to the sequences and saved. Images will linked into Markdown
in the second column, after the "Button" column.

options:
  -h, --help            show this help message and exit
  --md-file MD_FILE     Input filename for the Markdown file
  --md-out-file MD_OUT_FILE
                        Output filename for Input Markdown with updated image
                        links
  --image-out-dir IMAGE_OUT_DIR
                        Output directory name for composited images, will be
                        created (Default: 'out')
  --button-pattern-file BUTTON_PATTERN_FILE
                        Pattern filename for matching buttons (Default:
                        'qunmk2.patset')
  --image-height IMAGE_HEIGHT
                        Scale generated images to height (Default: 48)
  --print-formatted     Print formatted Input Markdown to stdout
  --print-extract       Print extracted buttons to stdout

Image generation data sources:
  {imageset,psd}        Optional subcommands for how to generate images: the
                        source of image data
    imageset            Use a directory of images for the layers
    psd                 NOT RECOMMENDED: Read image data from PSD file -
                        depends on Adobe(tm) Photoshop tech, slow,
                        incompatibilities between PSD tools yields un
```

## imageset

```
usage: mdpicgen imageset [-h] [--imageset-file IMAGESET_FILE]
                         [--imageset-dir IMAGESET_DIR]

options:
  -h, --help            show this help message and exit
  --imageset-file IMAGESET_FILE
                        Specifies what image filename will be used for what
                        layer, and their xy coordinates (Default:
                        'qunmk2_imageset.csv')
  --imageset-dir IMAGESET_DIR
                        Directory containing images used as layers defined in
                        '--imageset-file' (Default: 'imageset')
```

## psd

```
usage: mdpicgen psd [-h] --psd-file PSD_FILE

options:
  -h, --help           show this help message and exit
  --psd-file PSD_FILE  Input filename for the PSD file
```

## Origin

To help keep Markdown editing fun for projects needing to add many images which are permutations of a source diagram, this tool will do the heavy lifting.

It is designed for the needs of the Qun mk2 synthesizer project's [README.md](https://github.com/raspy135/Qun-mk2) guide documentation, originally. Adding images to the guide provides helpful visualizations to teach synthesizer control combinations. Users may refer to pictures in order to activate features on the synthesizer, in addition to text. There are many combinations available with the Qun, and many images to generate, consequently.

So updating 60+ structured images and their Markdown links is work worthy of automation.

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
* Update the original Markdown, and add missing or update outdated image links, without imposing auto-reformatting on potentially hand-edited (dense) tables

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
* Imagesets can be most image filetypes, and must have their layer information configured in an [imageset CSV](#imageset-CSV).
* PSD file must have a layer titled, `"BG"`. This will be composited behind all other layers during image generation.
* PSD file layer names must include short-names. These short-names must be located after a hyphen (-) in the layer name.
  * E.g. the `"s"` in the layer name, `"SHIFT - s"`
  * See also the [image name discussion](#generated-image-names).
* PSD layers **should** be rasterized, first. They may be vector layers and this may result in empty images being generated. Rasterizing can fix this issue in some cases. Overall, PSD files can be unexpectedly problematic.

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

# Imageset CSV

Encode filenames and layer names for all layers matchable in the [button pattern file](#button-pattern-file).

A default [imageset file](qunmk2_imageset.csv) and [directory](imageset) is provided for the Qun mk2 synthesizer.

# Examples

## Markdown sample: 

1. Notice the first row's header is `Button`. This matches the default [patset file](qunmk2.patset).
2. Notice the `<br>` tag is used only once
   1. With `--md-out-file`, an image link will be added, if missing.
   2. Or it will be updated, if already in the doc.
3. Notice the "B1", "SHIFT", etc are configured in the [patset file](qunmk2.patset).

```markdown
|               Button               | Description                         |
|:----------------------------------:|-------------------------------------|
| B1 + B2 <br> ![](./doc/sample.png) | A button sequence and image         |
|          SHIFT + B3 <br>           | No image. Will injected with image. |
|              SYS + B4              | No br-tag. Won't receive image.     |
```

## At command line -- show program options, verbosely

* `python3 __main__.py`, or `python3 __main__.py -h`

## Generate images for a Markdown file to the default `out` directory

* `python3 __main__.py --md-file test.md imageset`

and for the Qun mk2 project:

* `python3 __main__.py --md-file ../Qun-mk2/README.md --image-out-dir ../Qun-mk2/manual_images/but --image-height 56 imageset --imageset-file qunmk2_imageset.csv --imageset-dir imageset`

## Add and update image links to a new Markdown file

* `python3 __main__.py --md-file test.md --md-out-file out_test_md.md`
  
and for the Qun mk2 project:

* `python3 __main__.py --md-file ../Qun-mk2/README.md --md-out-file ../Qun-mk2/README-merge_me.md`

## Print all found button sequences from a Markdown file

* `python3 __main__.py --md-file test.md --print-extract`

## Read a custom button pattern file, and find button sequences in a Markdown file

* `python3 __main__.py --md-file test.md --print-extract --button-pattern-file custom.patset`

## Utility to format and print a Markdown file

* `python3 __main__.py --md-file test.md --print-formatted`

# Limitations

* Only one `<br>` tag should be present in a cell for a matching table's first-column. With `--md-out-file`, each br-tag will result in a new image added to the Markdown.

# Requirements

* python 3.10+
* psd-tools 1.9
* pillow - image manipulation
* mistletoe 1.3 - Markdown parsing

## Thanks

* Wow Python, such easy, much functionality
* Google + Gemini AI for teaching me moar Python and helping me design the tool. 
  * Details: suggested names for this tool, wrote initial versions of many functions, introduced me to many basic packages + helped me choose 3rd party libraries, gave me sample code for each, suggested high-level project organization, 

# Development 

## Future

### ~~Alternative image sources~~

**DONE** imageset support added. 114 times faster than PSD.

### Column two, three (etc.) image placements 

Currently, column one is the only column for image extraction and placement. Markdown tables can be written with, or without boundary edge markers (|), which complicates parsing.
* **Solution**: Support arbitrary columns by leveraging [mistletoe](#requirements) to first format and normalize Markdown tables in-memory, then I may rely upon a regular table row boundary pattern and make changes, leveraging that and the non-whitespace elements to inject / update image links, preserving the original non-auto-formatted Markdown's look

### Animated GIFs and more: press-duration visualization of buttons

* Currently, a static PNG is generated illustrating the original Markdown documentation's chord of buttons needing pressing e.g. to initiate a feature. Occasionally button presses requre holding for a longer duration than just a moment, and there is no way to represent this with a static image.
* **Idea**:
  * Take a button sequence with `"(Long press)"` instructions and make a GIF out of it, _flashing buttons with a given timing_. And, take multistep sequences which involve pressing the same button multiple times, and represent those with flashing. Pillow library can generate GIFs from source images. 
  * A simpler approach to _statically represent the duration_, and repeated pressing, could be used. This could suffer from visual over-complication, becoming more distracting than educational. 
    * E.g. to illustrate this, activated buttons could also have a double-outline, or perhaps an asterisk shaped flare of rays emerging from underneath the button for long-press, and a super-script dot to indicate the number of repeated presses required. 
    * Appropriately, sheet music has the concept of [long press](https://en.wikipedia.org/wiki/Note_value) and also [repeating phrases](https://en.wikipedia.org/wiki/Repeat_sign). So it may be worthwhile to consider their conceits.
  * A _combination approach_ could be used, also where the first frame of the GIF is the static image and subsequent frames flash buttons. This might dazzle the reader more than help. Though in my opinion utility of productivity is over-emphasized - the challenging [form follows function](https://en.wikipedia.org/wiki/Form_follows_function) practice, in short.
