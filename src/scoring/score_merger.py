"""
Merge text-derived scores into chunk metadata.

This module joins per-chunk text feature scores with the primary
chunk metadata to prepare for final scoring.
"""

import json
from pathlib import Path

from infra.config import CHUNKS_DIR, DATA_DIR


# Path to persisted text feature scores
TEXT_FEATURES_PATH = DATA_DIR / "text_features.json"


def merge_text_scores_into_chunks():
    """
    Attach text scores to corresponding chunk entries.

    For each chunk:
    - Looks up text-derived features using the chunk filename stem
    - Writes a `text_score` field into chunk metadata
    - Defaults to 0.0 when no text features are available

    Returns:
        Updated list of chunk metadata dictionaries.

    Raises:
        RuntimeError: If required metadata files are missing.
    """
    chunks_path = CHUNKS_DIR / "chunks.json"

    if not chunks_path.exists():
        raise RuntimeError("chunks.json not found")

    if not TEXT_FEATURES_PATH.exists():
        raise RuntimeError("text_features.json not found")

    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    with open(TEXT_FEATURES_PATH, "r", encoding="utf-8") as f:
        text_features = json.load(f)

    for entry in chunks:
        chunk_stem = Path(entry["file"]).stem
        text_data = text_features.get(chunk_stem)

        if text_data:
            entry["text_score"] = float(text_data.get("text_score", 0.0))
        else:
            entry["text_score"] = 0.0

    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2)

    return chunks
