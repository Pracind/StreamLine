import json
from infra.config import CHUNKS_DIR, CHAT_METRICS_DIR
from infra.config import ENABLE_CHAT_INFLUENCE
from infra.logger import setup_logger

CHAT_BOOST_MAX = 0.25  # hard safety cap


def apply_chat_boost_to_chunks(logger):


    if not ENABLE_CHAT_INFLUENCE:
        return
    
    chunks_path = CHUNKS_DIR / "chunks.json"
    chat_path = CHAT_METRICS_DIR / "chat_scores_aligned.json"

    if not chunks_path.exists():
        raise RuntimeError("chunks.json not found")

    if not chat_path.exists():
        # Chat is optional — Phase 1 still works
        return

    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    with open(chat_path, "r", encoding="utf-8") as f:
        chat_data = json.load(f)

    chat_by_sec = {
        item["video_second"]: item["score"]
        for item in chat_data["timeline"]
    }

    for entry in chunks:
        start = int(entry["start_sec"])
        end = int(entry["end_sec"])

        # Phase 1 baseline (guaranteed)
        base = entry.get("phase1_score", entry["final_score"])

        # Max chat score within chunk window
        chat_boost = 0.0
        for sec in range(start, end + 1):
            chat_boost = max(chat_boost, chat_by_sec.get(sec, 0.0))

        chat_boost = min(chat_boost, CHAT_BOOST_MAX)

        # Additive, never destructive
        entry["chat_boost"] = chat_boost
        entry["final_score"] = min(1.0, base + chat_boost)

        logger.info(
            "Chunk %s | phase1=%.3f chat=%.3f final=%.3f",
            entry.get("file", "unknown"),
            base,
            chat_boost,
            entry["final_score"],
        )

    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2)
