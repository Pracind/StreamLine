import json
from pathlib import Path

import whisper

from src.config import (
    AUDIO_DIR,
    TRANSCRIPTS_DIR,
    WHISPER_MODEL_NAME,
    CHUNKS_DIR
)


def transcribe_audio_chunks():
    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    clear_existing_transcripts()

    audio_files = sorted(AUDIO_DIR.glob("chunk_*.wav"))

    if not audio_files:
        raise RuntimeError("No audio files found for transcription.")

    model = whisper.load_model(WHISPER_MODEL_NAME)

    results = {}

    for audio_path in audio_files:
        transcript_path = TRANSCRIPTS_DIR / f"{audio_path.stem}.json"

        # Cache: skip if already transcribed
        if transcript_path.exists():
            with open(transcript_path, "r", encoding="utf-8") as f:
                results[audio_path.stem] = json.load(f)
            continue

        try:
            result = model.transcribe(
                str(audio_path),
                fp16=False,
            )
        except Exception as e:
            print(f"ERROR: Transcription failed for {audio_path.name}")
            print(str(e))
            raise SystemExit(1)

        transcript_data = {
            "text": result.get("text", "").strip(),
            "segments": result.get("segments", []),
            "language": result.get("language"),
        }

        with open(transcript_path, "w", encoding="utf-8") as f:
            json.dump(transcript_data, f, indent=2)

        results[audio_path.stem] = transcript_data

    return results




def clear_existing_transcripts():
    for file in TRANSCRIPTS_DIR.glob("chunk_*.json"):
        file.unlink()