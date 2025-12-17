import json
from pathlib import Path

from src.config import CHUNKS_DIR, AUDIO_WEIGHT, TEXT_WEIGHT


def compute_final_score(audio_score: float, text_score: float) -> float:
    return (
        AUDIO_WEIGHT * audio_score
        + TEXT_WEIGHT * text_score
    )


def apply_final_scores_to_chunks():
    chunks_path = CHUNKS_DIR / "chunks.json"

    if not chunks_path.exists():
        raise RuntimeError("chunks.json not found")

    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    for entry in chunks:
        audio_score = float(entry.get("audio_score", 0.0))
        text_score = float(entry.get("text_score", 0.0))

        entry["final_score"] = compute_final_score(
            audio_score=audio_score,
            text_score=text_score,
        )

    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2)

    return chunks
