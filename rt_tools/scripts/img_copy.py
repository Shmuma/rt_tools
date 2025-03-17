"""
Utility copies front covers into separate directory
"""
import pathlib
import argparse
import shutil

DEFAULT_FILE_NAME = "Front.jpeg"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", help="Name of directory to store front covers", required=True)
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

    out_path = pathlib.Path(args.output)
    if not out_path.exists():
        out_path.mkdir(parents=True)

    for dir in dirs:
        f_path = dir / args.name
        if not f_path.exists():
            print("Skipping " + str(dir))
        else:
            d_name = dir.name.split(" ")[0]
            d_path = out_path / (d_name + ".jpeg")
            shutil.copy(f_path, d_path)
            print(f"{f_path} -> {d_path}")

    return 0


if __name__ == "__main__":
    main()
