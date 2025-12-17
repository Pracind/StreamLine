import subprocess
import json
from pathlib import Path

from src.config import CHUNK_DURATION_SECONDS, CHUNKS_DIR


def chunk_video(input_video_path: str, logger):
    logger.info(f"Starting video chunking: {input_video_path}")

    metadata_path = CHUNKS_DIR / "chunks.json"

    if metadata_path.exists():
        existing_chunks = list(CHUNKS_DIR.glob("chunk_*.mp4"))
        if existing_chunks:
            logger.info("Chunks already exist — skipping video chunking")
            with open(metadata_path, "r", encoding="utf-8") as f:
                return json.load(f)

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

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        logger.exception("FFmpeg failed during video chunking")
        raise RuntimeError("Video chunking failed") from e

    chunk_files = sorted(CHUNKS_DIR.glob("chunk_*.mp4"))

    if not chunk_files:
        logger.error("Chunking completed but no chunks were created")
        raise RuntimeError("No chunks created from input video")

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

    logger.info(
        f"Video chunking complete: {len(chunk_files)} chunks created "
        f"({CHUNK_DURATION_SECONDS}s each)"
    )
    logger.info(f"Chunk metadata written to {metadata_path}")

    return metadata


def clear_existing_chunks():
    for file in CHUNKS_DIR.glob("chunk_*.mp4"):
        file.unlink()
