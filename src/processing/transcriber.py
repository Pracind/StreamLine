import json
from pathlib import Path

import whisper

from infra.config import (
    AUDIO_DIR,
    TRANSCRIPTS_DIR,
    WHISPER_MODEL_NAME,
    CHUNKS_DIR
)


def transcribe_audio_chunks(logger, resume: bool):
    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    if not resume:
        clear_existing_transcripts()
    else:
        logger.info("Using cached transcripts (resume enabled)")

    audio_files = sorted(AUDIO_DIR.glob("chunk_*.wav"))

    if not audio_files:
        logger.error("No audio files found for transcription")
        raise RuntimeError("No audio files found for transcription")

    total = len(audio_files)
    logger.info(f"Loading Whisper model: {WHISPER_MODEL_NAME}")
    model = whisper.load_model(WHISPER_MODEL_NAME)

    results = {}

    logger.info(f"Starting transcription for {total} audio files")

    for idx, audio_path in enumerate(audio_files, start=1):
        transcript_path = TRANSCRIPTS_DIR / f"{audio_path.stem}.json"

        # Cache hit
        if transcript_path.exists():
            logger.info(
                f"Whisper [{idx}/{total}] cache hit: {audio_path.name}"
            )
            with open(transcript_path, "r", encoding="utf-8") as f:
                results[audio_path.stem] = json.load(f)
            continue

        logger.info(
            f"Whisper [{idx}/{total}] transcribing {audio_path.name}"
        )

        try:
            result = model.transcribe(
                str(audio_path),
                fp16=False,
            )
        except Exception as e:
            logger.exception(
                f"Transcription failed for {audio_path.name}"
            )
            raise RuntimeError(
                f"Transcription failed for {audio_path.name}"
            ) from e

        transcript_data = {
            "text": result.get("text", "").strip(),
            "segments": result.get("segments", []),
            "language": result.get("language"),
        }

        with open(transcript_path, "w", encoding="utf-8") as f:
            json.dump(transcript_data, f, indent=2)

        results[audio_path.stem] = transcript_data

    logger.info("Transcription completed successfully")

    return results




def clear_existing_transcripts():
    for file in TRANSCRIPTS_DIR.glob("chunk_*.json"):
        file.unlink()