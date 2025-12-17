import json
import subprocess
from pathlib import Path
import shutil

from src.config import DATA_DIR


HIGHLIGHTS_DIR = DATA_DIR / "highlights"
TIMELINE_PATH = HIGHLIGHTS_DIR / "highlight_timeline_final.json"

OUTPUT_DIR = DATA_DIR / "output" / "clips"


def extract_highlight_clips(input_video: Path):
    if not TIMELINE_PATH.exists():
        raise RuntimeError("highlight_timeline_final.json not found")


    with open(TIMELINE_PATH, "r", encoding="utf-8") as f:
        highlights = json.load(f)

    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    extracted = []

    for idx, h in enumerate(highlights):
        start = h["start_time"]
        end = h["end_time"]
        duration = end - start

        output_path = OUTPUT_DIR / f"highlight_{idx:03d}.mp4"

        command = [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel", "error",
            "-fflags", "+genpts",
            "-ss", str(start),
            "-i", str(input_video),
            "-t", str(duration),
            "-c", "copy",
            str(output_path),
        ]

        subprocess.run(command, check=True)

        extracted.append(str(output_path))

    return extracted
