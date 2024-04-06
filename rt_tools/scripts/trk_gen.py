"""
Utility to generate rutracker classical music release from tracks files
"""
import argparse
import pathlib
import datetime
import typing as tt
from rt_tools.durations import get_flac_duration, duration_to_min_sec, duration_to_hms
from rt_tools.titles import ComposersMode, TitlesGenerator


def iterate_dirs(path: pathlib.Path) -> tt.List[pathlib.Path]:
    """
    Find all paths which looks like directories with flac files
    :param path: path to process
    :return: list of paths
    """
    paths = set()
    for f in path.glob("**/*.flac"):
        paths.add(f.parent)
    return list(sorted(set(paths)))


def generate_dir(dir: pathlib.Path, calc_duration: bool = False) -> datetime.timedelta:
    res = datetime.timedelta()
    files = []

    for f in sorted(dir.glob("*.flac")):
        files.append(f)
        if calc_duration:
            duration = get_flac_duration(f)
            res += duration

    length_part = ""
    if calc_duration:
        min, sec = duration_to_min_sec(res)
        length_part = f" - [{min}:{sec:02}]"

    titles_gen = TitlesGenerator(ComposersMode.Prepend, separators=[", ", ": ", "- "])
    print(f'[spoiler="{dir.name}{length_part}"]')
    for idx, f in enumerate(files, start=1):
        name = f.name
        v = name.split(".", maxsplit=1)
        if len(v) > 1:
            name = v[1].strip()
        for l in titles_gen.add_track(idx, "", name):
            print(l)

    ac_log = dir / "audiochecker.log"
    if ac_log.exists():
        print('\n[spoiler="Лог проверки качества"][pre]')
        print(ac_log.read_text())
        print('[/pre][/spoiler]')

    dr_files = list(dir.glob("dr14*.txt"))
    if dr_files:
        print('\n[spoiler="Динамический отчет (dr14-tmeter)"][pre]')
        print(dr_files[0].read_text())
        print('[/pre][/spoiler]')
    print('[/spoiler]\n')

    return res


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--duration", action='store_true', default=False,
                        help="Use ffprobe to get duration of flac files")
    parser.add_argument("input", nargs="+", help="Directory to process")
    args = parser.parse_args()
    duration = datetime.timedelta()

    dirs_list = []
    for in_name in args.input:
        in_path = pathlib.Path(in_name)
        dirs_list.extend(iterate_dirs(in_path))
    dirs_list.sort()

    for dir in dirs_list:
        duration += generate_dir(dir, calc_duration=args.duration)

    if args.duration:
        hour, min, sec = duration_to_hms(duration)
        print(f"Total duration: {hour}:{min:02}:{sec:02}")


if __name__ == "__main__":
    main()