import sys
import os

from mdpicgen import (format_markdown, process_psd, process_imageset, extract_button_sequences, write_markdown,
                      ImageOpt, write_seqs_markdown)

DEBUG_LOG_MAIN = True

if __name__ == '__main__':
    import argparse

    script_dir = os.path.dirname(os.path.realpath(__file__))

    # n.b. use Unix command `fold` to format full (-h) usage for pasting into README.md
    #   python3 ../mdpicgen -h | fold | pbcopy
    #   python3 ../mdpicgen imageset -h | fold | pbcopy
    #   python3 ../mdpicgen psd -h | fold | pbcopy

    parser = argparse.ArgumentParser(
        description='''Parse Markdown table cells into recognized sequences of strings, "keys". 
                    Only matches keys from table columns all identified by patterns in the button-pattern-file.
                    Inserts and updates links for image files to output Markdown in the cells after the keys.
                    Creates a sequence-only Markdown with tables categorizing the sequences. 
                    Generate images using image layers, named based upon the keys 
                    -- see sub-commands for image generation details. 
                    ''')

    parser.add_argument("--md-file", type=str, help="Input filename for the Markdown file.", required=True)
    parser.add_argument("--md-out-file", type=str,
                        help="Output filename for Input Markdown with updated image links.")
    parser.add_argument("--md-seqs-out-file", type=str,
                        help="Output filename for sequence-only Markdown, with categorized tables of button sequences "
                             "and image links.")
    parser.add_argument("--image-out-dir", default='out', type=str,
                        help="Output directory name for composited images, will be created (Default: 'out').")

    parser.add_argument("--button-pattern-file", default=f"{script_dir}/qunmk2.patset", type=str,
                        help="Pattern filename for matching buttons (Default: 'qunmk2.patset').")
    parser.add_argument("--category-pattern-file", default=f"f{script_dir}/qunmk2_categories.csv", 
                        type=str, help="Category pattern filename for organizing sequences "
                                       "(Default: 'qunmk2_categories.csv').")

    parser.add_argument("--image-height", default=48, type=int,
                        help="Pixel height of generated images, used with sub-commands (Default: 48).")
    parser.add_argument("--gif", action='store_true',
                        help="Generate GIF from button sequences, sets filename extension (Default: false, use PNG).")

    parser.add_argument("--print-formatted", action='store_true',
                        help="Print formatted Markdown (from '--md-file') to the console.")
    parser.add_argument("--print-extract", action='store_true', help="Print sequences to console.")

    # Image sources are mutually exclusive commands with multiple parameters

    subparsers = parser.add_subparsers(dest="image_source", required=False,
                                       title="Image generation sub-commands",
                                       help="Optional sub-commands for how to generate images: "
                                            "the source of image data.")

    parser_imageset = subparsers.add_parser("imageset",
                                            help="Read image data from a directory of images, supports GIF animation "
                                                 "of button sequences.")
    parser_imageset.add_argument("--imageset-file", type=str,
                                 help="Specifies what image filename will be used for what layer, "
                                      "and their xy coordinates."
                                      "(Default: 'qunmk2_imageset.csv')",
                                 default='qunmk2_imageset.csv')
    parser_imageset.add_argument("--imageset-dir", type=str, default="imageset",
                                 help="Directory containing images used as layers defined in '--imageset-file'"
                                      " (Default: 'imageset').")

    parser_psd = subparsers.add_parser("psd",
                                       help="NOT RECOMMENDED: Read image data from PSD file. "
                                            "depends on Adobe(tm) Photoshop tech, slow, "
                                            "incompatibilities between PSD tools unexpectedly breaks workflows, "
                                            "animation not supported.")
    parser_psd.add_argument("--psd-file", type=str, help="Input filename for the PSD file.", required=True)

    args = parser.parse_args()

    # Extract from Markdown
    button_sequences = []
    try:
        button_sequences = extract_button_sequences(args.md_file, args.button_pattern_file)
        print(f"extracted {len(button_sequences)} sequences")
    except Exception as e:
        print(f"Aborting. Error extracting button sequences: {e}", file=sys.stderr)
        # exit(1)
        raise e

    basenames = [seq.basename for seq in button_sequences]

    if args.print_extract:
        for seq in button_sequences:
            print(f"{seq.sequence_mapping} => {seq.basename}")

    if args.image_source == "psd" and args.psd_file:
        try:
            if args.gif:
                print("Ignoring --gif option, unsupported for PSD", file=sys.stderr)

            process_psd(args.image_out_dir, args.psd_file, basenames, args.image_height)
        except Exception as e:
            print(f"Aborting. Error processing PSD file: {e}", file=sys.stderr)
            exit(1)
    elif args.image_source == "imageset":
        try:
            process_imageset(args.image_out_dir, args.imageset_file, args.imageset_dir, button_sequences,
                             ImageOpt(height=args.image_height, gif=args.gif))
        except Exception as e:
            print(f"Aborting. Error processing imageset: {e}", file=sys.stderr)
            exit(1)

    if args.md_out_file:
        try:
            markdown = write_markdown(args.md_out_file, args.image_out_dir, args.md_file, button_sequences,
                                      ImageOpt(args.image_height, gif=args.gif))
        except Exception as e:
            print(f"Aborting. Error writing markdown: {e}", file=sys.stderr)
            exit(1)

    if args.md_seqs_out_file:
        try:
            markdown = write_seqs_markdown(args.md_seqs_out_file, args.image_out_dir, args.md_file, 
                                           args.category_pattern_file, button_sequences,
                                           ImageOpt(args.image_height, gif=args.gif))
        except Exception as e:
            print(f"Aborting. Error writing markdown: {e}", file=sys.stderr)
            
            ### TODO UNCOMMENT
            # exit(1)

            ## REMOVEME
            raise e

    if args.print_formatted:
        formatted_text = format_markdown(args.md_file)
        print(formatted_text)
