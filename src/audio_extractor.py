import subprocess
from pathlib import Path
import sys

from src.config import AUDIO_DIR, AUDIO_SAMPLE_RATE, CHUNKS_DIR


def extract_audio_from_chunks():
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    chunk_files = sorted(CHUNKS_DIR.glob("chunk_*.mp4"))

    if not chunk_files:
        print("No video chunks found to extract audio from.")
        sys.exit(1)

    extracted_count = 0

    for chunk_path in chunk_files:
        audio_filename = chunk_path.stem + ".wav"
        audio_output_path = AUDIO_DIR / audio_filename

        command = [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel", "error",
            "-i", str(chunk_path),
            "-vn",
            "-ac", "1",
            "-ar", str(AUDIO_SAMPLE_RATE),
            "-f", "wav",
            str(audio_output_path),
        ]

        try:
            subprocess.run(command, check=True)
            extracted_count += 1

        except subprocess.CalledProcessError as e:
            print(f"ERROR: Failed to extract audio from {chunk_path.name}")
            print("FFmpeg exited with a non-zero status.")
            sys.exit(1)

        except Exception as e:
            print(f"UNEXPECTED ERROR while processing {chunk_path.name}")
            print(str(e))
            sys.exit(1)

    return extracted_count
