import enum
import typing as tt


class ComposersMode(enum.Enum):
    Prepend = "prepend"
    Inside = "inside"
    Nothing = "nothing"

    @classmethod
    def values(cls) -> tt.Tuple[str, ...]:
        return tuple(p.value for p in cls)


def split_piece_part(title: str) -> tt.Tuple[tt.Optional[str], str]:
    parts = title.split(" - ", maxsplit=1)
    if len(parts) == 1:
        return None, title
    return parts[0], parts[1]


class TitlesGenerator:
    def __init__(self, composers_mode: ComposersMode):
        self._composers_mode = composers_mode
        self._composer = None
        self._piece = None

    def add_track(self, num: int, composer: str, title: str) -> tt.Generator[str, None, None]:
        if self._composers_mode == ComposersMode.Inside:
            yield f"{num}. {composer}: {title}"
            return
        elif self._composers_mode == ComposersMode.Nothing:
            yield f"{num}. {title}"
            return

        separator_shown = False
        if self._composer is None or self._composer != composer:
            separator_shown = True
            if self._composer is not None:
                yield ""
            yield composer
            self._composer = composer
        piece, part = split_piece_part(title)
        if piece is not None and piece != self._piece:
            if not separator_shown:
                if self._piece is None or self._piece != piece:
                    yield ""
            yield piece
            self._piece = piece
        elif piece is None:
            self._piece = None
        yield f"{num}. {part}"


def group_performers(performers: tt.List[str]) -> tt.Generator[str, None, None]:
    cur_perf = None
    cur_start = None
    groups = []

    for idx, perf in enumerate(performers, start=1):
        if cur_perf is None:
            cur_start = idx
            cur_perf = perf
            continue
        elif cur_perf == perf:
            continue
        else:
            groups.append((cur_start, idx-1, cur_perf))
            cur_start = idx
            cur_perf = perf
    if not groups and cur_perf is not None:
        # only one performer - just yield it
        yield cur_perf
        return

    groups.append((cur_start, len(performers), cur_perf))
    for start, stop, perf in groups:
        if start != stop:
            yield f"{start}-{stop}. {perf}"
        else:
            yield f"{start}. {perf}"
