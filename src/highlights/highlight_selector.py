"""
Flag chunk entries as highlights based on scoring thresholds.

This module performs the initial binary highlight classification step by
evaluating phase-1 scores, final boosted scores, and optional chat-only
signals against configured thresholds.
"""

import json

from infra.config import (
    CHUNKS_DIR,
    HIGHLIGHT_THRESHOLD,
    ENABLE_CHAT_ONLY_HIGHLIGHTS,
    CHAT_ONLY_THRESHOLD,
)


def flag_highlight_chunks():
    """
    Determine which chunks qualify as highlights.

    A chunk is marked as a highlight if any of the following are true:
    - Phase-1 score exceeds the highlight threshold
    - Final score (after chat boost) exceeds the highlight threshold
    - Chat-only mode is enabled and chat boost exceeds its threshold

    The function annotates each chunk with:
    - `is_highlight`: boolean classification
    - `highlight_reason`: primary reason for highlight selection

    Returns:
        Number of chunks flagged as highlights.
    """
    chunks_path = CHUNKS_DIR / "chunks.json"

    if not chunks_path.exists():
        raise RuntimeError("chunks.json not found")

    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    highlight_count = 0

    for entry in chunks:
        # Extract score components with backward-compatible fallbacks
        phase1_score = float(
            entry.get("phase1_score", entry.get("final_score", 0.0))
        )
        final_score = float(entry.get("final_score", 0.0))
        chat_boost = float(entry.get("chat_boost", 0.0))

        # Independent highlight qualification checks
        is_phase1 = phase1_score >= HIGHLIGHT_THRESHOLD
        is_chat_boosted = final_score >= HIGHLIGHT_THRESHOLD

        # Optional chat-only highlight path
        is_chat_only = (
            ENABLE_CHAT_ONLY_HIGHLIGHTS
            and not is_phase1
            and not is_chat_boosted
            and chat_boost >= CHAT_ONLY_THRESHOLD
        )

        entry["is_highlight"] = is_phase1 or is_chat_boosted or is_chat_only