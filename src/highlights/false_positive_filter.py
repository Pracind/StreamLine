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
    chunks_path = CHUNKS_DIR / "chunks.json"

    if not chunks_path.exists():
        raise RuntimeError("chunks.json not found")

    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    for i, entry in enumerate(chunks):
        if not entry.get("is_highlight"):
            continue

        phase1 = float(entry.get("phase1_score", entry.get("final_score", 0.0)))
        chat = float(entry.get("chat_boost", 0.0))
        text = float(entry.get("text_score", 0.0))
        final = float(entry.get("final_score", 0.0))

        # ── Filter 1: weak single-signal highlights ──
        strong_signals = sum([
            phase1 >= PHASE1_STRONG_THRESHOLD,
            chat >= CHAT_STRONG_THRESHOLD,
            text >= TEXT_STRONG_THRESHOLD,
        ])

        if strong_signals == 0:
            entry["is_highlight"] = False
            entry["filtered_reason"] = "weak_single_signal"
            continue

        # ── Filter 2: isolated highlights ──
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

        # ── Filter 3: chat-only safety gate ──
        if (
            entry.get("highlight_reason") == "chat_only"
            and final < CHAT_ONLY_MIN_SCORE
        ):
            entry["is_highlight"] = False
            entry["filtered_reason"] = "weak_chat_only"

    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2)
