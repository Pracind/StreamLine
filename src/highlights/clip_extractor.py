"""
Extract per-highlight video clips from the source video.

This module reads the finalized highlight timeline and uses FFmpeg
to cut exact time ranges into individual clip files. It supports
resume semantics to avoid re-extracting clips that already exist.
"""

import json
import subprocess
from pathlib import Path
import shutil

from infra.config import DATA_DIR


# Directory containing the finalized highlight timeline
HIGHLIGHTS_DIR = DATA_DIR / "highlights"
TIMELINE_PATH = HIGHLIGHTS_DIR / "highlight_timeline_final.json"

# Output directory for extracted highlight clips
OUTPUT_DIR = DATA_DIR / "output" / "clips"


def extract_highlight_clips(input_video: Path, logger, resume: bool):
    """
    Extract highlight clips from the input video using a finalized timeline.

    For each highlight entry in the timeline:
    - Computes the clip duration
    - Uses FFmpeg to perform a stream-copy extraction
    - Optionally skips clips that already exist when resume=True

    Args:
        input_video: Path to the source video file.
        logger: Logger instance for progress and error reporting.
        resume: If True, reuse existing clip files when present.

    Returns:
        List of Paths to extracted (or reused) clip files.

    Raises:
        RuntimeError: If the highlight timeline is missing or extraction fails.
    """


    
    if not TIMELINE_PATH.exists():
        logger.error("highlight_timeline_final.json not found")
        raise RuntimeError("highlight_timeline_final.json not found")

    with open(TIMELINE_PATH, "r", encoding="utf-8") as f:
        highlights = json.load(f)

    total = len(highlights)
    logger.info(f"Starting clip extraction for {total} highlights")

    # Clear previous outputs unless explicitly resuming
    if OUTPUT_DIR.exists() and not resume:
        shutil.rmtree(OUTPUT_DIR)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    extracted = []

    for idx, h in enumerate(highlights, start=1):
        output_path = OUTPUT_DIR / f"highlight_{idx - 1:03d}.mp4"

        # Resume logic: skip extraction if clip already exists
        if resume and output_path.exists():
            logger.info(
                f"Clip [{idx}/{total}] cache hit: {output_path.name}"
            )
            extracted.append(output_path)
            continue

        start = h["start_time"]
        end = h["end_time"]
        duration = end - start

        logger.info(
            f"Clip [{idx}/{total}] extracting "
            f"{start:.2f}s → {end:.2f}s"
        )

        # FFmpeg command for lossless segment extraction
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

        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            logger.exception(
                f"Clip extraction failed: {output_path.name}"
            )
            raise RuntimeError(
                f"Clip extraction failed for {output_path.name}"
            ) from e

        extracted.append(output_path)

    logger.info(f"Clip extraction complete: {len(extracted)}/{total}")

    return extracted
