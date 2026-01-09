import json
from pathlib import Path

from infra.config import CHUNKS_DIR, DATA_DIR, MERGE_GAP_SECONDS
from highlights.timeline_io import save_timeline

HIGHLIGHTS_DIR = DATA_DIR / "highlights"
TIMELINE_PATH = HIGHLIGHTS_DIR / "highlight_timeline.json"


def merge_adjacent_highlights():
    chunks_path = CHUNKS_DIR / "chunks.json"

    if not chunks_path.exists():
        raise RuntimeError("chunks.json not found")

    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    highlight_chunks = [c for c in chunks if c.get("is_highlight")]

    if not highlight_chunks:
        save_timeline(TIMELINE_PATH, {"schema_version": 2, "timeline": []})
        return []

    highlight_chunks.sort(key=lambda c: c["start_time"])

    merged = []
    current = {
        "start_time": highlight_chunks[0]["start_time"],
        "end_time": highlight_chunks[0]["end_time"],
        "chunk_ids": [highlight_chunks[0]["chunk_id"]],
    }

    for chunk in highlight_chunks[1:]:
        if chunk["start_time"] <= current["end_time"] + MERGE_GAP_SECONDS:
            current["end_time"] = max(current["end_time"], chunk["end_time"])
            current["chunk_ids"].append(chunk["chunk_id"])
        else:
            merged.append(current)
            current = {
                "start_time": chunk["start_time"],
                "end_time": chunk["end_time"],
                "chunk_ids": [chunk["chunk_id"]],
            }

    merged.append(current)

    # Build v2 timeline with defaults
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
