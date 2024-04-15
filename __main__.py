from psd_in_md import format_markdown, process_psd, extract_buttons

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='''Read Markdown and process PSD, generating images and inserting / updating into Markdown.
                    PSD layer names will be used as keys. 
                    They will be matched to formatted key sequences found in Markdown tables with 
                    first columns labelled \"Button\".
                    Layers will be composited into images according to the sequences and saved. 
                    Images will linked into Markdown in the second column, after the \"Button\" column. 
                    Markdown will be dumped to stdout.
                    ''')

    parser.add_argument("md_file", type=str, help="Input filename for the Markdown file")
    parser.add_argument("--button-pattern-file", type=str, help="Pattern filename for matching buttons",
                        default="qunmk2_button_patterns.txt")

    parser.add_argument("--psd-file", type=str, help="Input filename for the PSD file")
    parser.add_argument("--psd-out-dir", default='out', type=str,
                        help="Output directory name for composited images, will be created (Default: 'out')")

    parser.add_argument("--print-formatted", action='store_true', help="Print formatted Markdown to stdout")
    parser.add_argument("--print-extract", action='store_true', help="Print extracted buttons to stdout")

    args = parser.parse_args()

    extracted_buttons = extract_buttons(args.md_file, args.button_pattern_file)
    if args.print_extract:
        print(extracted_buttons)
        print(f"found: {len(extracted_buttons)}")

    if args.psd_file:
        try:
            process_psd(args.psd_out_dir, args.md_file, args.psd_file)
        except Exception as e:
            print(f"Error processing PSD file: {e}")
            exit(1)

    formatted_text = format_markdown(args.md_file)
    if args.print_formatted:
        print(formatted_text)
