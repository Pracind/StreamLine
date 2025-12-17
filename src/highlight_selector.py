import json

from src.config import CHUNKS_DIR, HIGHLIGHT_THRESHOLD


def flag_highlight_chunks():
    chunks_path = CHUNKS_DIR / "chunks.json"

    if not chunks_path.exists():
        raise RuntimeError("chunks.json not found")

    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    highlight_count = 0

    for entry in chunks:
        final_score = float(entry.get("final_score", 0.0))

        is_highlight = final_score >= HIGHLIGHT_THRESHOLD
        entry["is_highlight"] = is_highlight

        if is_highlight:
            highlight_count += 1

    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2)

    return highlight_count
