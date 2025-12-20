import json
from pathlib import Path

from src.infra.config import (
    DATA_DIR,
    MIN_HIGHLIGHT_DURATION_SECONDS,
)


HIGHLIGHTS_DIR = DATA_DIR / "highlights"
BUFFERED_PATH = HIGHLIGHTS_DIR / "highlight_timeline_buffered.json"
FILTERED_PATH = HIGHLIGHTS_DIR / "highlight_timeline_final.json"


def filter_short_highlights():
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

    with open(FILTERED_PATH, "w", encoding="utf-8") as f:
        json.dump(kept, f, indent=2)

    return kept
