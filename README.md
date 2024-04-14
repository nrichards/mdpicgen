# psd-in-md

Helps keep Markdown editing fun.

Automates maintenance of Markdown files. Generates and inserts images into a specially formatted Markdown.

## Origin

To help keep Markdown editing fun, this tool aims to alleviate some of the cost of creating standardized but customized images used in technical manuals.

Specifically this is designed for the needs of the Qun mk2 synthesizer project's [README.md](https://github.com/raspy135/Qun-mk2) guide. Images are helpful visualizations to teach synthesizer control combinations which users memorize in order to activate features on the synthesizer. Updating the images and the Markdown is work which is worthy of automation.

| Generated                |
|--------------------------|
| ![](./doc/s_splay_d.png) |

# Features (WIP)

* Extract sequences of names of button controls from formatted Markdown
  * Names of controls are grouped in a sequence. E.g. "SHIFT + B1".
  * The sequence is then parsed to individual button names, e.g. "SHIFT" and "B1"
  * Names **MUST** be located in the first column of tables 
  * Tables **MUST** have a first column name of "`Button`"
  * Tables **MUST** be at least three columns wide 
* Generate images by compositing a set of layers of a diagram based upon the button control sequence's names 
  * Names may differ from the names used for the diagram layers. A mapping between the user-facing formatted sequence naming and the layers is implemented here.
  * Images are sized down to fit in tables
* Update the original Markdown with generated images
  * Automates inserting Markdown image links into the corresponding table lines' second column 

# Usage

Run from the command line.

* `python3 __main__.py` - shows options
* `python3 __main__.py test.md --psd_out_dir out --psd_file test.psd` - formats Markdown file, generates image to the `out` directory

# Requirements

* python 3.6+
* psd-tools 1.9

# Development notes

* "Not fun" warning ... 
  * Working with Photoshop PSD files is proving problematic due to compatibility issues. Everyone involved in the project does not own a license from Adobe and instead uses their own PSD editor. Also, the Python libraries to extract PSD data have their own issues, following Adobe's out-of-date and wrong specification, plus they are maintained by volunteers who may not have motivation to solve my particular compatibility issues. 
  * Solution will be to migrate to 100% Python compositing. Ideas include:
    * JSON file dictating layout of named button controls
    * Layout could specify shapes and colors, e.g. "rectangle" and "orange". Shape drawing commands could then render the stylized shapes, and save the final image.
    * Or, layout could use pre-built images, and specify location, image-name, and orientation. Drawing commands could render the component images by placement, and then save the final image.
* Neat: Command to extract the text from the first column of 3+ column tables:

```shell
grep "|.*|" full.md | grep -v -e "^-" -e "^Button" | \
  sed 's/\([^|]*\)|.*/\1/g' | sort -u
```
