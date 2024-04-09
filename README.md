# psd-in-md

Automates maintenance of Markdown files. Generates and inserts images into a specially formatted Markdown file.

Designed for the needs of the Qun mk2 synthesizer project's [README.md](https://github.com/raspy135/Qun-mk2) guide. Images are helpful visualizations to teach synthesizer control combinations which users memorize in order to activate features on the synthesizer. Updating the images and the Markdown is work which is worthy of automation.

# Features (WIP)

* Extract sequences of names of controls from formatted Markdown
  * Names of controls are grouped in a sequence. The sequence is then
  * Names **MUST** be located in the first column of tables 
    * Tables **MUST** have a first column name of "`Button`"
    * Tables **MUST** be at least three columns wide 
* Generate images composited from a set of layers of a PSD file based upon control sequence's names extracted from the Markdown file
  * Names may differ from the names used for the layers in the PSD file. A mapping between the user-facing formatted sequence naming and the PSD layers is implemented here.
  * Images are sized down to fit in tables
* Update the original Markdown with generated images
  * Automates inserting Markdown image links into the corresponding table lines' second column 

# Usage

Run from the command line.

`python3 -m psd-in-md`

Find output files in the `out` directory.

* TODO: Specify the Markdown file
* TODO: Specify the PSD file

# Requirements

* python 3.6+
* psd-tools 1.9

# Development notes

Command to extract the text from the first column of 3+ column tables:

```shell
grep "|.*|" full.md | grep -v -e "^-" -e "^Button" | \
  sed 's/\([^|]*\)|.*/\1/g' | sort -u
```
