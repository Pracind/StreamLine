"""
Merge adjacent highlight chunks into continuous highlight intervals.

This module groups consecutive or near-consecutive highlight-marked chunks
into higher-level highlight segments and emits a structured v2 timeline.
"""

import json
from pathlib import Path

from infra.config import CHUNKS_DIR, DATA_DIR, MERGE_GAP_SECONDS
from highlights.timeline_io import save_timeline


# Directory containing highlight timeline artifacts
HIGHLIGHTS_DIR = DATA_DIR / "highlights"

# Output path for the merged highlight timeline
TIMELINE_PATH = HIGHLIGHTS_DIR / "highlight_timeline.json"


def merge_adjacent_highlights():
    """
    Merge temporally adjacent highlight chunks into contiguous intervals.

    Two highlight chunks are merged if the gap between them is less than or
    equal to MERGE_GAP_SECONDS. The result is emitted as a v2 highlight
    timeline with stable IDs and default editing metadata.

    Returns:
        List of merged highlight timeline entries.
    """
    chunks_path = CHUNKS_DIR / "chunks.json"

    if not chunks_path.exists():
        raise RuntimeError("chunks.json not found")

    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    # Select only chunks flagged as highlights
    highlight_chunks = [c for c in chunks if c.get("is_highlight")]

    # Handle empty highlight set explicitly
    if not highlight_chunks:
        save_timeline(TIMELINE_PATH, {"schema_version": 2, "timeline": []})
        return []

    # Ensure deterministic merge order
    highlight_chunks.sort(key=lambda c: c["start_time"])

    merged = []

    # Initialize the first merge window
    current = {
        "start_time": highlight_chunks[0]["start_time"],
        "end_time": highlight_chunks[0]["end_time"],
        "chunk_ids": [highlight_chunks[0]["chunk_id"]],
    }

    for chunk in highlight_chunks[1:]:
        # Extend current window if within merge gap
        if chunk["start_time"] <= current["end_time"] + MERGE_GAP_SECONDS:
            current["end_time"] = max(current["end_time"], chunk["end_time"])
            current["chunk_ids"].append(chunk["chunk_id"])
        else:
            # Finalize current window and start a new one
            merged.append(current)
            current = {
                "start_time": chunk["start_time"],
                "end_time": chunk["end_time"],
                "chunk_ids": [chunk["chunk_id"]],
            }

    merged.append(current)

    # Build v2 timeline entries with default editing metadata
    timeline = []
    for idx, item in enumerate(merged):
        timeline.append({
            "id": f"hl_{idx:04d}",
            "start_time": float(item["start_time"]),
            "end_time": float(item["end_time"]),
            "chunk_ids": list(item.get("chunk_ids", [])),
            "enabled": True,
            "trim_start_offset": 0.0,
            "trim_end_offset": 0.0,
            "order_index": idx,
        })

    save_timeline(TIMELINE_PATH, {"schema_version": 2, "timeline": timeline})
    return timeline
