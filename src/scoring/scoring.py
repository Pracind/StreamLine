"""
Core phase-1 scoring logic.

This module combines audio and text-derived scores into an initial
phase-1 score that serves as the baseline for highlight selection
and downstream boosting.
"""

import json
from pathlib import Path

from infra.config import CHUNKS_DIR, AUDIO_WEIGHT, TEXT_WEIGHT


def compute_final_score(audio_score: float, text_score: float) -> float:
    """
    Compute the phase-1 score from audio and text components.

    The score is a weighted linear combination of the two inputs
    using globally configured weights.
    """
    return (
        AUDIO_WEIGHT * audio_score
        + TEXT_WEIGHT * text_score
    )


def apply_final_scores_to_chunks():
    """
    Apply phase-1 scoring to all chunks.

    This function:
    - Reads chunk metadata
    - Computes a phase-1 score from audio and text scores
    - Initializes both `phase1_score` and `final_score` fields
      (the latter may be modified later by chat boosting)

    Returns:
        Updated list of chunk metadata dictionaries.

    Raises:
        RuntimeError: If chunk metadata is missing.
    """
    chunks_path = CHUNKS_DIR / "chunks.json"

    if not chunks_path.exists():
        raise RuntimeError("chunks.json not found")

    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    for entry in chunks:
        audio_score = float(entry.get("audio_score", 0.0))
        text_score = float(entry.get("text_score", 0.0))

        phase1 = compute_final_score(
            audio_score=audio_score,
            text_score=text_score,
        )

        entry["phase1_score"] = phase1
        entry["final_score"] = phase1

    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2)

    return chunks
