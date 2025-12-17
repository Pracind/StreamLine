import json
from pathlib import Path

from src.config import (
    DATA_DIR,
    PRE_BUFFER_SECONDS,
    POST_BUFFER_SECONDS,
)


HIGHLIGHTS_DIR = DATA_DIR / "highlights"
TIMELINE_PATH = HIGHLIGHTS_DIR / "highlight_timeline.json"
BUFFERED_PATH = HIGHLIGHTS_DIR / "highlight_timeline_buffered.json"


def add_buffers_to_highlights():
    if not TIMELINE_PATH.exists():
        raise RuntimeError("highlight_timeline.json not found")

    with open(TIMELINE_PATH, "r", encoding="utf-8") as f:
        highlights = json.load(f)

    buffered = []

    for h in highlights:
        start = max(0, h["start_time"] - PRE_BUFFER_SECONDS)
        end = h["end_time"] + POST_BUFFER_SECONDS

        buffered.append({
            "start_time": start,
            "end_time": end,
            "chunk_ids": h.get("chunk_ids", []),
            "buffered": True,
        })

    with open(BUFFERED_PATH, "w", encoding="utf-8") as f:
        json.dump(buffered, f, indent=2)

    return buffered
