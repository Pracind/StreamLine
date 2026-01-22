"""
Extract audio tracks from chunked video segments.

This module converts each video chunk into a corresponding WAV audio file,
optionally reusing existing outputs when resume mode is enabled.
"""

import subprocess
from pathlib import Path
import sys

from infra.config import AUDIO_DIR, AUDIO_SAMPLE_RATE, CHUNKS_DIR


def extract_audio_from_chunks(logger, resume: bool):
    """
    Extract PCM audio from each video chunk using FFmpeg.

    For each chunk:
    - Produces a WAV file with the same base name
    - Skips extraction when resume=True and the audio file already exists

    Args:
        logger: Logger instance for progress and error reporting.
        resume: If True, reuse previously extracted audio files.

    Returns:
        Number of audio files successfully extracted.
    """
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    if not resume:
        clear_existing_audio()

    chunk_files = sorted(CHUNKS_DIR.glob("chunk_*.mp4"))

    if not chunk_files:
        logger.error("No video chunks found to extract audio from")
        raise RuntimeError("No video chunks found")

    total = len(chunk_files)
    extracted_count = 0

    for idx, chunk_path in enumerate(chunk_files, start=1):
        audio_output_path = AUDIO_DIR / f"{chunk_path.stem}.wav"

        # Resume logic: skip extraction if output already exists
        if resume and audio_output_path.exists():
            logger.info(
                f"Audio [{idx}/{total}] cache hit: {audio_output_path.name}"
            )
            extracted_count += 1
            continue

        logger.info(
            f"Audio [{idx}/{total}] extracting from {chunk_path.name}"
        )

        # FFmpeg command for audio-only extraction
        command = [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel", "error",
            "-i", str(chunk_path),
            "-vn",
            "-acodec", "pcm_s16le",
            str(audio_output_path),
        ]

        try:
            subprocess.run(command, check=True)
            extracted_count += 1
        except subprocess.CalledProcessError as e:
            logger.exception(
                f"Failed to extract audio from {chunk_path.name}"
            )
            raise RuntimeError(
                f"Audio extraction failed for {chunk_path.name}"
            ) from e

    logger.info(
        f"Audio extraction complete: {extracted_count}/{total} files"
    )

    return extracted_count


def clear_existing_audio():
    """
    Remove previously extracted audio files.

    This is used when resume mode is disabled to ensure a clean
    re-extraction of all audio artifacts.
    """
    for file in AUDIO_DIR.glob("chunk_*.wav"):
        file.unlink()
