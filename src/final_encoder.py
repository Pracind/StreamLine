import subprocess
from pathlib import Path

from src.config import DATA_DIR


INPUT_PATH = DATA_DIR / "output" / "highlights_raw.mp4"
OUTPUT_PATH = DATA_DIR / "output" / "highlights_final.mp4"


def encode_final_video():
    if not INPUT_PATH.exists():
        raise RuntimeError("highlights_raw.mp4 not found")

    command = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel", "error",
        "-i", str(INPUT_PATH),
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        str(OUTPUT_PATH),
    ]

    subprocess.run(command, check=True)

    return OUTPUT_PATH
