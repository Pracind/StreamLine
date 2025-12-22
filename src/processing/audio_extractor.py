import subprocess
from pathlib import Path
import sys

from infra.config import AUDIO_DIR, AUDIO_SAMPLE_RATE, CHUNKS_DIR


def extract_audio_from_chunks(logger, resume: bool):
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

        # ✅ RESUME LOGIC
        if resume and audio_output_path.exists():
            logger.info(
                f"Audio [{idx}/{total}] cache hit: {audio_output_path.name}"
            )
            extracted_count += 1
            continue

        logger.info(
            f"Audio [{idx}/{total}] extracting from {chunk_path.name}"
        )

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
    for file in AUDIO_DIR.glob("chunk_*.wav"):
        file.unlink()
