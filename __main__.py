# Import necessary functions from psd_in_md.py
from psd_in_md import format_markdown, process_psd

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Process PSD file and format text as markdown")
    parser.add_argument("--psd_file", type=str, help="Path to the PSD file")
    parser.add_argument("--md_file", type=str, help="Input filename for the markdown file (default: stdout)")
    parser.add_argument("--format", action="store_true", help="Format extracted text as markdown (default: False)")
    args = parser.parse_args()

    # Handle missing arguments gracefully
    if not any(vars(args).values()):
        parser.print_help()
        exit(1)

    # Process the PSD file
    if args.psd_file:
        try:
            process_psd(args.psd_file)
        except Exception as e:
            print(f"Error processing PSD file: {e}")
            exit(1)

    # Optionally format the extracted text
    if args.format:
        formatted_text = format_markdown(args.md_file)
        print(formatted_text)
