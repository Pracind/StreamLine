import json

from infra.config import (
    CHUNKS_DIR,
    HIGHLIGHT_THRESHOLD,
    ENABLE_CHAT_ONLY_HIGHLIGHTS,
    CHAT_ONLY_THRESHOLD,
)


def flag_highlight_chunks():
    chunks_path = CHUNKS_DIR / "chunks.json"

    if not chunks_path.exists():
        raise RuntimeError("chunks.json not found")

    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    highlight_count = 0

    for entry in chunks:
        phase1_score = float(
            entry.get("phase1_score", entry.get("final_score", 0.0))
        )
        final_score = float(entry.get("final_score", 0.0))
        chat_boost = float(entry.get("chat_boost", 0.0))

        is_phase1 = phase1_score >= HIGHLIGHT_THRESHOLD
        is_chat_boosted = final_score >= HIGHLIGHT_THRESHOLD

        is_chat_only = (
            ENABLE_CHAT_ONLY_HIGHLIGHTS
            and not is_phase1
            and not is_chat_boosted
            and chat_boost >= CHAT_ONLY_THRESHOLD
        )

        entry["is_highlight"] = is_phase1 or is_chat_boosted or is_chat_only

        if entry["is_highlight"]:
            highlight_count += 1
            
            if is_phase1:
                entry["highlight_reason"] = "phase1"
            elif is_chat_boosted:
                entry["highlight_reason"] = "chat_boost"
            else:
                entry["highlight_reason"] = "chat_only"

    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2)

    return highlight_count
