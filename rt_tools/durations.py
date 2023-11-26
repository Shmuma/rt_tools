import pathlib
import datetime
import subprocess
import typing as tt


def get_flac_duration(flac_path: pathlib.Path) -> datetime.timedelta:
    """
    Get duration of the flac file using ffprobe utility.
    :param flac_path: path to flac file
    :return: duration of flac file
    """
    output = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                                      "default=noprint_wrappers=1:nokey=1", str(flac_path)])
    return datetime.timedelta(seconds=float(output))


def duration_to_min_sec(duration: datetime.timedelta) -> tt.Tuple[int, int]:
    """
    Convert duration to minutes and seconds.
    :param duration: timedelta
    :return: tuple with minutes and seconds
    """
    total_sec = duration.total_seconds()
    return int(total_sec // 60), int(total_sec % 60)