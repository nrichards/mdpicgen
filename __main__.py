from mdpicgen import (format_markdown, process_psd, extract_button_sequences, format_image_basename, write_markdown,
                      ButtonSequence)
import sys
import os

DEBUG_LOG_MAIN = True

if __name__ == '__main__':
    import argparse

    script_dir = os.path.dirname(os.path.realpath(__file__))

    # n.b. use Unix command `fold` to format full (-h) usage for pasting into README.md
    parser = argparse.ArgumentParser(
        description='''Read Markdown and process image layers, generating images and inserting / updating into Markdown.
                    Layer names will be used as keys. 
                    They will be matched to formatted key sequences [configurable] found in Markdown tables with 
                    first columns labelled \"Button\" [also configurable].
                    Layers will be composited into images according to the sequences and saved. 
                    Images will linked into Markdown in the second column, after the \"Button\" column.
                    ''')

    parser.add_argument("--md-file", type=str, help="Input filename for the Markdown file", required=True)
    parser.add_argument("--md-out-file", type=str,
                        help="Output filename for Input Markdown with updated image links", )
    parser.add_argument("--image-out-dir", default='out', type=str,
                        help="Output directory name for composited images, will be created (Default: 'out')")

    parser.add_argument("--button-pattern-file", default=f"{script_dir}/qunmk2.patset", type=str,
                        help="Pattern filename for matching buttons (Default: 'qunmk2.patset')")

    parser.add_argument("--image-height", default=48, type=int,
                        help="Scale generated images to height (Default: 48)")

    parser.add_argument("--print-formatted", action='store_true',
                        help="Print formatted Input Markdown to stdout")
    parser.add_argument("--print-extract", action='store_true', help="Print extracted buttons to stdout")

    subparsers = parser.add_subparsers(dest="image_source", required=False,
                                       title="Image generation data sources",
                                       help="Optional subcommands for how to generate images: the source of image data")

    parser_imageset = subparsers.add_parser("imageset",
                                            help="Use a directory of images for the layers")
    parser_imageset.add_argument("--imageset-file", type=str,
                                 help="Specifies what image filename will be used for what layer, "
                                      "and their xy coordinates "
                                      "(Default: 'qunmk2_imageset.csv')",
                                 default='qunmk2_imageset.csv')
    parser_imageset.add_argument("--imageset-dir", type=str, default="imageset",
                                 help="Directory containing images used as layers defined in '--imageset-file'"
                                      " (Default: 'imageset')")

    parser_psd = subparsers.add_parser("psd",
                                       help="Read image data from PSD file - depends on Adobe(tm) Photoshop tech")
    parser_psd.add_argument("--psd-file", type=str, help="Input filename for the PSD file", required=True)

    args = parser.parse_args()

    # Extract from Markdown
    button_sequences = extract_button_sequences(args.md_file, args.button_pattern_file)

    if args.print_extract:
        for seq in button_sequences:
            print(f"{seq.sequence_mapping} => {seq.basename}")
        if DEBUG_LOG_MAIN:
            print(f"found: {len(button_sequences)}", file=sys.stderr)

    if args.image_source == "psd" and args.psd_file:
        try:
            basenames = [seq.basename for seq in button_sequences]
            process_psd(args.image_out_dir, args.psd_file, basenames, args.image_height)
        except Exception as e:
            print(f"Aborting. Error processing PSD file: {e}", file=sys.stderr)
            exit(1)

    if args.md_out_file:
        markdown = write_markdown(args.md_out_file, args.image_out_dir, args.md_file, button_sequences)

    if args.print_formatted:
        formatted_text = format_markdown(args.md_file)
        print(formatted_text)
