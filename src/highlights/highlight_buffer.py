"""
Apply temporal buffers to highlight intervals.

This module expands each highlight window by configurable pre- and post-
buffer durations to improve pacing and contextual continuity in the final
output video.
"""

import json
from pathlib import Path

from infra.config import (
    DATA_DIR,
    PRE_BUFFER_SECONDS,
    POST_BUFFER_SECONDS,
)


# Directory containing intermediate highlight timelines
HIGHLIGHTS_DIR = DATA_DIR / "highlights"

# Input timeline prior to buffering
TIMELINE_PATH = HIGHLIGHTS_DIR / "highlight_timeline.json"

# Output timeline with buffers applied
BUFFERED_PATH = HIGHLIGHTS_DIR / "highlight_timeline_buffered.json"


def add_buffers_to_highlights():
    """
    Expand highlight start and end times by fixed buffer durations.

    This function:
    - Loads the unbuffered highlight timeline
    - Applies pre- and post-buffers to each highlight interval
    - Normalizes older and newer timeline schemas
    - Writes the buffered timeline to disk

    Returns:
        List of buffered highlight interval dictionaries.
    """
    if not TIMELINE_PATH.exists():
        raise RuntimeError("highlight_timeline.json not found")

    with open(TIMELINE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Handle v2 timeline schema where highlights are nested under "timeline"
    if isinstance(data, dict) and "timeline" in data:
        highlights = data["timeline"]
    else:
        highlights = data

    buffered = []

    for h in highlights:
        # Apply temporal padding while clamping start to zero
        start = max(0, h["start_time"] - PRE_BUFFER_SECONDS)
        end = h["end_time"] + POST_BUFFER_SECONDS

        buffered.append({
            "start_time": start,
            "end_time": end,
            "chunk_ids": h.get("chunk_ids", []),
            "buffered": True,
        })

    # Persist buffered timeline
    with open(BUFFERED_PATH, "w", encoding="utf-8") as f:
        json.dump(buffered, f, indent=2)

    return buffered
