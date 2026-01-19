"""
Filter out highlight intervals that are too short to be meaningful.

This module enforces a minimum duration constraint on buffered highlights
and produces the final highlight timeline used for clip extraction.
"""

import json
from pathlib import Path

from infra.config import (
    DATA_DIR,
    MIN_HIGHLIGHT_DURATION_SECONDS,
)


# Directory containing highlight timeline artifacts
HIGHLIGHTS_DIR = DATA_DIR / "highlights"

# Input timeline after buffer expansion
BUFFERED_PATH = HIGHLIGHTS_DIR / "highlight_timeline_buffered.json"

# Final, duration-filtered highlight timeline
FILTERED_PATH = HIGHLIGHTS_DIR / "highlight_timeline_final.json"


def filter_short_highlights():
    """
    Remove buffered highlights shorter than the minimum allowed duration.

    This function:
    - Loads the buffered highlight timeline
    - Computes duration for each highlight
    - Retains only those meeting the configured duration threshold
    - Writes the final timeline to disk

    Returns:
        List of retained highlight interval dictionaries.
    """
    if not BUFFERED_PATH.exists():
        raise RuntimeError("highlight_timeline_buffered.json not found")

    with open(BUFFERED_PATH, "r", encoding="utf-8") as f:
        highlights = json.load(f)

    kept = []

    for h in highlights:
        duration = h["end_time"] - h["start_time"]

        if duration >= MIN_HIGHLIGHT_DURATION_SECONDS:
            h["duration"] = duration
            kept.append(h)

    # Persist the filtered highlight timeline
    with open(FILTERED_PATH, "w", encoding="utf-8") as f:
        json.dump(kept, f, indent=2)

    return kept
