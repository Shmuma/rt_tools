"""
Utility to generate rutracker classical music release from CUE files
"""
import enum
import argparse
import pathlib
import typing as tt
from rt_tools.cueparser import CueSheet
from rt_tools.titles import ComposersMode, TitlesGenerator, group_performers

HEADER_OUTPUT = "%performer% - %title%\n%file%\n%tracks%"
TRACK_OUTPUT = "%performer% - %title%"

PathCue = tt.Tuple[pathlib.Path, CueSheet]


class GenMode(enum.Enum):
    Full = 'full'
    Titles = 'titles'
    Logs = 'logs'

    @classmethod
    def values(cls) -> tt.Tuple[str, ...]:
        return tuple(v.value for v in cls)


def load_cue(cue_path: pathlib.Path) -> PathCue:
    cue = CueSheet()
    cue.setOutputFormat(HEADER_OUTPUT, TRACK_OUTPUT)
    cue.setData(cue_path.read_text('utf-8'))
    cue.parse()
    return cue_path, cue


def generate_titles(cue: CueSheet, composers_mode: ComposersMode, separators: tt.List[str]) -> tt.Generator[str, None, None]:
    perfs = []
    titles_gen = TitlesGenerator(composers_mode, separators=separators)
    for track in cue.tracks:
        perfs.append(track.performer)
        yield from titles_gen.add_track(track.number, track.songwriter, track.title)

    if perfs:
        yield ""
        yield "[b]Исполнители[/b]:"
        yield from group_performers(perfs)


def generate_logs(cue_path: pathlib.Path, cue: CueSheet) -> tt.Generator[str, None, None]:
    yield '[spoiler="Лог создания рипа"][pre]'
    log_path = cue_path.with_suffix(".log")
    yield log_path.read_text()
    yield '[/pre][/spoiler]'
    yield ''

    yield '[spoiler="Содержание индексной карты (.CUE)"][pre]'
    yield cue_path.read_text()
    yield '[/pre][/spoiler]'


def get_section_name(idx: int, path: pathlib.Path) -> str:
    # if path contains dir name, use dir name, otherwise just index
    if len(path.parts) > 1:
        return path.parts[-2]
    return f"CD{idx}"


def generate_output(mode: GenMode, paths_cues: tt.List[PathCue],
                    composers_mode: ComposersMode, separators: tt.List[str]) -> tt.Generator[str, None, None]:
    for idx, (path, cue) in enumerate(paths_cues, start=1):
        section_name = get_section_name(idx, path)
        length_part = ""
        if mode != GenMode.Logs:
            length_part = " - [:]"
        yield f'[spoiler="{section_name}{length_part}"]'
        if mode == GenMode.Titles:
            yield from generate_titles(cue, composers_mode=composers_mode, separators=separators)
        elif mode == GenMode.Full:
            yield from generate_titles(cue, composers_mode=composers_mode, separators=separators)
            yield ''
            yield from generate_logs(path, cue)
        elif mode == GenMode.Logs:
            yield from generate_logs(path, cue)
        yield '[/spoiler]'
        yield ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mode", choices=GenMode.values(), default=GenMode.Titles.value,
                        help="Mode of generation, default=" + GenMode.Titles.value)
    parser.add_argument("-c", "--composers", choices=ComposersMode.values(),
                        default=ComposersMode.Prepend.value,
                        help="Mode of composers generation, default=" + ComposersMode.Prepend.value)
    parser.add_argument("-o", "--output", help="Name of the output file. If not given, use stdout")
    parser.add_argument("--sep", action='append', default=[],
                        help="Optional separator of title parts, default=detect")
    parser.add_argument("input", nargs="+", help="Directory or CUE file to process")
    args = parser.parse_args()

    paths_cues = []
    for in_name in args.input:
        in_path = pathlib.Path(in_name)
        if in_path.is_file():
            paths_cues.append(load_cue(in_path))
        elif in_path.is_dir():
            for f in sorted(in_path.glob("**/*.cue")):
                paths_cues.append(load_cue(f))

    for l in generate_output(GenMode(args.mode), paths_cues,
                             composers_mode=ComposersMode(args.composers),
                             separators=args.sep):
        print(l)
    return 0


if __name__ == "__main__":
    main()