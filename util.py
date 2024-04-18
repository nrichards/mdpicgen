from pathlib import Path


def make_out_dir(out_dirname):
    Path(out_dirname).mkdir(parents=True, exist_ok=True)
