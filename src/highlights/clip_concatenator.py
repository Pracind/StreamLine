import subprocess
from pathlib import Path

from src.infra.config import DATA_DIR


CLIPS_DIR = DATA_DIR / "output" / "clips"
OUTPUT_PATH = DATA_DIR / "output" / "highlights_raw.mp4"
FILELIST_PATH = DATA_DIR / "output" / "concat_list.txt"


def concatenate_clips():
    clips = sorted(CLIPS_DIR.glob("highlight_*.mp4"))

    if not clips:
        raise RuntimeError("No highlight clips found to concatenate")

    # Write concat file list
    with open(FILELIST_PATH, "w", encoding="utf-8") as f:
        for clip in clips:
            # FFmpeg concat demuxer requires this exact format
            f.write(f"file '{clip.resolve().as_posix()}'\n")

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
