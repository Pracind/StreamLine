import subprocess
import json
from pathlib import Path

from src.config import CHUNK_DURATION_SECONDS, CHUNKS_DIR


def chunk_video(input_video_path: str):
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

    clear_existing_chunks()

    chunk_pattern = str(CHUNKS_DIR / "chunk_%04d.mp4")

    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "error",
        "-i", input_video_path,
        "-map", "0",
        "-c", "copy",
        "-f", "segment",
        "-segment_time", str(CHUNK_DURATION_SECONDS),
        "-reset_timestamps", "1",
        chunk_pattern,
    ]

    subprocess.run(command, check=True)

    chunk_files = sorted(CHUNKS_DIR.glob("chunk_*.mp4"))

    metadata = []
    for idx, chunk_file in enumerate(chunk_files):
        start_time = idx * CHUNK_DURATION_SECONDS
        end_time = start_time + CHUNK_DURATION_SECONDS

        metadata.append({
            "chunk_id": idx,
            "file": str(chunk_file),
            "start_time": start_time,
            "end_time": end_time,
        })

    metadata_path = CHUNKS_DIR / "chunks.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    return metadata


def clear_existing_chunks():
    for file in CHUNKS_DIR.glob("chunk_*.mp4"):
        file.unlink()
