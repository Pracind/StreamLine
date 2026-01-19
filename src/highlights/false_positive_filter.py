"""
Post-processing filters to remove false-positive highlight flags.

This module applies conservative, rule-based sanity checks on chunks that
were previously marked as highlights, demoting those that appear weak,
isolated, or insufficiently reinforced by multiple signals.
"""

import json
from infra.config import (
    CHUNKS_DIR,
    HIGHLIGHT_THRESHOLD,
    PHASE1_STRONG_THRESHOLD,
    CHAT_STRONG_THRESHOLD,
    TEXT_STRONG_THRESHOLD,
    CHAT_ONLY_MIN_SCORE,
)


def filter_false_positive_highlights():
    """
    Remove low-confidence highlight flags from chunk metadata.

    This function operates in-place on chunks.json and applies three
    sequential filters:
    1. Reject highlights without any strong contributing signal.
    2. Reject isolated spikes lacking reinforcement from neighbors.
    3. Apply a safety gate for chat-only highlights.

    Chunks failing any filter are demoted by clearing `is_highlight`
    and annotating a `filtered_reason` field.
    """

    
    chunks_path = CHUNKS_DIR / "chunks.json"

    if not chunks_path.exists():
        raise RuntimeError("chunks.json not found")

    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    for i, entry in enumerate(chunks):
        # Skip chunks that were never marked as highlights
        if not entry.get("is_highlight"):
            continue

        # Extract relevant score components with safe fallbacks
        phase1 = float(entry.get("phase1_score", entry.get("final_score", 0.0)))
        chat = float(entry.get("chat_boost", 0.0))
        text = float(entry.get("text_score", 0.0))
        final = float(entry.get("final_score", 0.0))

        # ── Filter 1: Weak single-signal highlights ────────────────────────────
        # Require at least one signal to exceed its "strong" threshold
        strong_signals = sum([
            phase1 >= PHASE1_STRONG_THRESHOLD,
            chat >= CHAT_STRONG_THRESHOLD,
            text >= TEXT_STRONG_THRESHOLD,
        ])

        if strong_signals == 0:
            entry["is_highlight"] = False
            entry["filtered_reason"] = "weak_single_signal"
            continue

        # ── Filter 2: Isolated highlight spikes ────────────────────────────────
        # A highlight must be reinforced by at least one neighboring chunk
        neighbors = []
        if i > 0:
            neighbors.append(chunks[i - 1])
        if i < len(chunks) - 1:
            neighbors.append(chunks[i + 1])

        reinforced = any(
            float(n.get("final_score", 0.0)) >= HIGHLIGHT_THRESHOLD * 0.9
            for n in neighbors
        )

        if not reinforced:
            entry["is_highlight"] = False
            entry["filtered_reason"] = "isolated_spike"
            continue

        # ── Filter 3: Chat-only safety gate ────────────────────────────────────
        # Enforce a minimum absolute score for chat-driven highlights
        if (
            entry.get("highlight_reason") == "chat_only"
            and final < CHAT_ONLY_MIN_SCORE
        ):
            entry["is_highlight"] = False
            entry["filtered_reason"] = "weak_chat_only"

    # Persist filtered results back to chunk metadata
    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2)
