from pathlib import Path
import sys

from src.config import INPUT_DIR
from src.config import CHUNKS_DIR
from src.video_chunker import chunk_video


def get_input_video() -> Path:
    if not INPUT_DIR.exists():
        print(f"Input directory does not exist: {INPUT_DIR}")
        sys.exit(1)

    video_files = list(INPUT_DIR.glob("*.mp4"))

    if not video_files:
        print("No input video found in data/input/")
        print("Please place an .mp4 file in the input directory.")
        sys.exit(1)

    if CHUNKS_DIR.exists() and any(CHUNKS_DIR.iterdir()):
        print("Warning: Existing chunks will be overwritten.")

    # Phase 1 assumption: single input video
    return video_files[0]


if __name__ == "__main__":
    input_video = get_input_video()
    print(f"Using input video: {input_video}")

    chunks = chunk_video(str(input_video))
    print(f"Created {len(chunks)} chunks.")
