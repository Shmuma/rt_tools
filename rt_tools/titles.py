import enum
import typing as tt


class ComposersMode(enum.Enum):
    Prepend = "prepend"
    Inside = "inside"
    Nothing = "nothing"

    @classmethod
    def values(cls) -> tt.Tuple[str, ...]:
        return tuple(p.value for p in cls)


def split_piece_part(title: str, separators: tt.List[str]) -> tt.Tuple[tt.Optional[str], str]:
    for sep in separators:
        parts = title.split(sep, maxsplit=1)
        if len(parts) == 2:
            return parts[0], parts[1]
    return None, title


class TitlesGenerator:
    DEFAULT_SEPARATORS = (": ", " - ")

    def __init__(self, composers_mode: ComposersMode, separators: tt.List[str]):
        self._composers_mode = composers_mode
        self._separators = separators if separators else self.DEFAULT_SEPARATORS
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
            yield f"[size=16]{composer}[/size]"
            self._composer = composer
        piece, part = split_piece_part(title, separators=self._separators)
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
