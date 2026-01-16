"""
Concatenate individual highlight clips into a single output video.

This module relies on FFmpeg's concat demuxer to perform a stream-copy
concatenation, assuming all input clips share identical codecs and
encoding parameters.
"""

import subprocess
from pathlib import Path

from infra.config import DATA_DIR


# Directory containing per-highlight video clips
CLIPS_DIR = DATA_DIR / "output" / "clips"

# Final concatenated output video (pre-final-encoding stage)
OUTPUT_PATH = DATA_DIR / "output" / "highlights_raw.mp4"

# Temporary FFmpeg concat file list
FILELIST_PATH = DATA_DIR / "output" / "concat_list.txt"


def concatenate_clips():
    """
    Concatenate all generated highlight clips into a single video file.

    The function:
    - Discovers highlight clips using a fixed filename pattern
    - Writes an FFmpeg-compatible concat file list
    - Executes FFmpeg in stream-copy mode to avoid re-encoding

    Raises:
        RuntimeError: If no highlight clips are found.
    """


    
    clips = sorted(CLIPS_DIR.glob("highlight_*.mp4"))

    if not clips:
        raise RuntimeError("No highlight clips found to concatenate")

    # Write FFmpeg concat demuxer file list
    with open(FILELIST_PATH, "w", encoding="utf-8") as f:
        for clip in clips:
            # FFmpeg concat demuxer requires absolute POSIX paths in this format
            f.write(f"file '{clip.resolve().as_posix()}'\n")

    # FFmpeg command for lossless clip concatenation
    command = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel", "error",
        "-f", "concat",
        "-safe", "0",
        "-i", str(FILELIST_PATH),
        "-c", "copy",
        str(OUTPUT_PATH),
    ]

    subprocess.run(command, check=True)

    return OUTPUT_PATH
