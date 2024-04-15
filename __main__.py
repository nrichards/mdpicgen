from psd_in_md import (format_markdown, process_psd, extract_button_sequences, format_image_basename, write_markdown,
                       ButtonSequence)
import sys

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='''Read Markdown and process PSD, generating images and inserting / updating into Markdown.
                    PSD layer names will be used as keys. 
                    They will be matched to formatted key sequences [configurable] found in Markdown tables with 
                    first columns labelled \"Button\" [also configurable].
                    Layers will be composited into images according to the sequences and saved. 
                    Images will linked into Markdown in the second column, after the \"Button\" column. 
                    Markdown will be dumped to stdout.
                    ''')

    parser.add_argument("md_file", type=str, help="Input filename for the Markdown file")
    parser.add_argument("--button-pattern-file", default="qunmk2.patset", type=str,
                        help="Pattern filename for matching buttons (Default: 'qunmk2.patset')")
    parser.add_argument("--md-out-file", type=str,
                        help="Output filename for Input Markdown with updated image links", )

    parser.add_argument("--psd-file", type=str, help="Input filename for the PSD file")
    parser.add_argument("--psd-out-dir", default='out', type=str,
                        help="Output directory name for composited images, will be created (Default: 'out')")
    parser.add_argument("--image-height", default=48, type=int,
                        help="Scale generated images to height (Default: 48)")

    parser.add_argument("--print-formatted", action='store_true',
                        help="Print formatted Input Markdown to stdout")
    parser.add_argument("--print-extract", action='store_true', help="Print extracted buttons to stdout")

    args = parser.parse_args()

    # Extract from Markdown
    button_sequences = extract_button_sequences(args.md_file, args.button_pattern_file)

    # Compute image basenames
    buttons = ButtonSequence.to_sequence_mapping_list(button_sequences)
    extracted_basenames = []
    for extract in buttons:
        image_basename = format_image_basename(extract)
        extracted_basenames = extracted_basenames + [image_basename]

    if args.print_extract:
        for (extract, image_basename) in zip(buttons, extracted_basenames):
            print(f"{extract} => {image_basename}")
        print(f"found: {len(buttons)}", file=sys.stderr)

    if args.psd_file:
        try:
            process_psd(args.psd_out_dir, args.psd_file, extracted_basenames, args.image_height)
        except Exception as e:
            print(f"Error processing PSD file: {e}", file=sys.stderr)
            exit(1)

    if args.md_out_file:
        markdown = write_markdown(args.md_out_file, args.md_file, button_sequences)
        print(markdown)

    if args.print_formatted:
        formatted_text = format_markdown(args.md_file)
        print(formatted_text)
