"""
Utility copies front covers into separate directory
"""
import pathlib
import argparse

DEFAULT_FILE_NAME = "Front.jpeg"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", help="Name of directory to store front covers")
    parser.add_argument("-n", "--name", help="Name of the file to copy, default=" + DEFAULT_FILE_NAME,
                        default=DEFAULT_FILE_NAME)
    parser.add_argument("input", nargs="+", help="Directory or cue path to process")
    args = parser.parse_args()

    dirs = []
    for in_name in args.input:
        in_path = pathlib.Path(in_name)
        if in_path.is_file():
            dirs.append(in_path.parent)
        elif in_path.is_dir():
            for f in sorted(in_path.glob("**/*.cue")):
                dirs.append(f.parent)

    print(dirs)

    return 0


if __name__ == "__main__":
    main()