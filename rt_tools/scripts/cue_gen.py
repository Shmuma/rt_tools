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


class GenModes(enum.Enum):
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


def generate_titles(cue: CueSheet, composers_mode: ComposersMode) -> tt.Generator[str, None, None]:
    perfs = []
    titles_gen = TitlesGenerator(composers_mode)
    for track in cue.tracks:
        perfs.append(track.performer)
        yield from titles_gen.add_track(track.number, track.songwriter, track.title)

    if perfs:
        yield ""
        yield "[b]Исполнители[/b]:"
        yield from group_performers(perfs)

def get_section_name(idx: int, path: pathlib.Path) -> str:
    # if path contains dir name, use dir name, otherwise just index
    if len(path.parts) > 1:
        return path.parts[-2]
    return f"CD{idx}"


def generate_output(mode: str, paths_cues: tt.List[PathCue],
                    composers_mode: ComposersMode) -> tt.Generator[str, None, None]:
    for idx, (path, cue) in enumerate(paths_cues, start=1):
        section_name = get_section_name(idx, path)
        yield f'[spoiler="{section_name} - [:]"]'
        if mode == 'titles':
            yield from generate_titles(cue, composers_mode=composers_mode)
        yield '[/spoiler]'


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mode", choices=GenModes.values(), default=GenModes.Titles.value,
                        help="Mode of generation, default=" + GenModes.Titles.value)
    parser.add_argument("-c", "--composers", choices=ComposersMode.values(),
                        default=ComposersMode.Prepend.value,
                        help="Mode of composers generation, default=" + ComposersMode.Prepend.value)
    parser.add_argument("-o", "--output", help="Name of the output file. If not given, use stdout")
    parser.add_argument("input", nargs="+", help="Directory or CUE file to process")
    args = parser.parse_args()

    paths_cues = []
    for in_name in args.input:
        in_path = pathlib.Path(in_name)
        if in_path.is_file():
            paths_cues.append(load_cue(in_path))

    for l in generate_output(args.mode, paths_cues, composers_mode=ComposersMode(args.composers)):
        print(l)
    return 0


if __name__ == "__main__":
    main()