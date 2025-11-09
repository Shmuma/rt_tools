"""
Utility to generate rutracker classical music release from CUE files
"""
import datetime
import enum
import argparse
import pathlib
import typing as tt
from rt_tools.cueparser import CueSheet
from rt_tools.titles import ComposersMode, TitlesGenerator, group_performers
from rt_tools.durations import get_flac_duration, duration_to_min_sec

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
        performer = track.performer
        composer = track.songwriter
        if performer is not None and ';' in performer:
            comp, performer = performer.split(';', maxsplit=1)
            performer = performer.strip()
            if composer is None:
                composer = comp
        perfs.append(performer)
        yield from titles_gen.add_track(track.number, composer, track.title)

    if perfs:
        yield ""
        yield "[b]Исполнители[/b]:"
        yield from group_performers(perfs)


def generate_logs(cue_path: pathlib.Path, cue: CueSheet) -> tt.Generator[str, None, None]:
    yield '[spoiler="Лог создания рипа"][pre]'
    log_path = cue_path.with_suffix(".log")
    try:
        text = log_path.read_text()
    except UnicodeDecodeError:
        text = log_path.read_text(encoding='utf-16')
    yield text
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


def generate_output(
        mode: GenMode, paths_cues: tt.List[PathCue],
        composers_mode: ComposersMode, separators: tt.List[str],
        calculate_duration: bool = False,
        front_urls: tt.Optional[tt.List[str]] = None,
) -> tt.Generator[str, None, None]:
    total_duration = datetime.timedelta()
    for idx, (path, cue) in enumerate(paths_cues, start=1):
        section_name = get_section_name(idx, path)
        length_part = ""
        duration = None
        if calculate_duration:
            flac_path = path.with_suffix(".flac")
            duration = get_flac_duration(flac_path)
            total_duration += duration
        if mode != GenMode.Logs:
            if duration is None:
                length_part = " - [:]"
            else:
                min, sec = duration_to_min_sec(duration)
                length_part = f" - [{min}:{sec:02}]"
        yield f'[spoiler="{section_name}{length_part}"]'

        if front_urls is not None:
            url = front_urls[idx-1]
            yield f"[img=right]{url}[/img]"

        if mode == GenMode.Titles:
            yield from generate_titles(cue, composers_mode=composers_mode, separators=separators)
        elif mode == GenMode.Full:
            yield from generate_titles(cue, composers_mode=composers_mode, separators=separators)
            yield ''
            yield from generate_logs(path, cue)
        elif mode == GenMode.Logs:
            yield from generate_logs(path, cue)

        for dr14_path in path.parent.glob("dr14*.txt"):
            yield '[spoiler="Динамический отчет (DR)"][pre]'
            yield dr14_path.read_text()[1:-1]
            yield '[/pre][/spoiler]'
            yield ""
            break

        yield '[/spoiler]'
        yield ""

    if calculate_duration:
        min, sec = duration_to_min_sec(total_duration)
        hour = 0
        if min > 60:
            hour = min // 60
            min %= 60
        yield f"Total duration: {hour}:{min:02}:{sec:02}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mode", choices=GenMode.values(), default=GenMode.Titles.value,
                        help="Mode of generation, default=" + GenMode.Titles.value)
    parser.add_argument("-c", "--composers", choices=ComposersMode.values(),
                        default=ComposersMode.Prepend.value,
                        help="Mode of composers generation, default=" + ComposersMode.Prepend.value)
    parser.add_argument("--sep", action='append', default=[],
                        help="Optional separator of title parts, default=detect")
    parser.add_argument("--duration", action='store_true', default=False,
                        help="Use ffprobe to get duration of flac file")
    parser.add_argument("--fronts", help="Optional filename with url of front images to be inserted")
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

    front_urls = None
    if args.fronts is not None:
        p = pathlib.Path(args.fronts)
        front_urls = [u for u in p.read_text().splitlines() if u]

    for l in generate_output(GenMode(args.mode), paths_cues,
                             composers_mode=ComposersMode(args.composers),
                             separators=args.sep,
                             calculate_duration=args.duration,
                             front_urls=front_urls):
        print(l)
    return 0


if __name__ == "__main__":
    main()
