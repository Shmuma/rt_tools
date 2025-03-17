Various utilities for RuTracker


# cue_gen

Generates spoilers data from image+.cue rip dirs.

Modes of operation (given with `-m` parameter):
* `full`: every cue produces separate spoiler with tracks, performers, logs and cues sections
* `titles`: (default) every cue produces just tracks and performers sections
* `logs`: every cue produces logs and cues spoilers

# img_copy

Copies front images from individual CD folders into one dir.
Useful to prepare list of front urls for cue_gen tool