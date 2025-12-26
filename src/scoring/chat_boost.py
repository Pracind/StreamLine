import json
from infra.config import CHUNKS_DIR, CHAT_METRICS_DIR
from infra.config import ENABLE_CHAT_INFLUENCE
from infra.config import MIN_CHAT_MESSAGES_PER_CHUNK, MIN_CHAT_ACTIVE_SECONDS_PER_CHUNK

CHAT_BOOST_MAX = 0.25  # hard safety cap


def apply_chat_boost_to_chunks(logger):
    try:
        if not ENABLE_CHAT_INFLUENCE:
            logger.info("Chat influence disabled — skipping chat boost")
            return

        mps_path = CHAT_METRICS_DIR / "messages_per_second.json"
        chat_scores_path = CHAT_METRICS_DIR / "chat_scores_aligned.json"
        chunks_path = CHUNKS_DIR / "chunks.json"

        if not mps_path.exists():
            logger.warning("messages_per_second.json not found — skipping chat boost")
            return

        if not chat_scores_path.exists():
            logger.warning("chat_scores_aligned.json not found — skipping chat boost")
            return

        if not chunks_path.exists():
            raise RuntimeError("chunks.json not found")

        logger.info("Applying chat boost to chunks")

        with open(mps_path, "r", encoding="utf-8") as f:
            mps_data = json.load(f)

        mps_by_sec = {
            int(item["second"]): int(item["messages"])
            for item in mps_data.get("timeline", [])
        }

        with open(chat_scores_path, "r", encoding="utf-8") as f:
            chat_data = json.load(f)

        chat_by_sec = {
            int(item["video_second"]): float(item["score"])
            for item in chat_data.get("timeline", [])
        }

        with open(chunks_path, "r", encoding="utf-8") as f:
            chunks = json.load(f)

        for entry in chunks:
            start = int(entry["start_time"])
            end = int(entry["end_time"])

            base = float(entry.get("phase1_score", entry.get("final_score", 0.0)))

            if not chat_is_significant(start, end, mps_by_sec):
                entry["chat_boost"] = 0.0
                entry["final_score"] = base
                entry["chat_suppressed"] = True
                continue

            chat_boost = 0.0
            for sec in range(start, end + 1):
                chat_boost = max(chat_boost, chat_by_sec.get(sec, 0.0))

            chat_boost = min(chat_boost, CHAT_BOOST_MAX)

            entry["chat_boost"] = chat_boost
            entry["final_score"] = min(1.0, base + chat_boost)
            entry["chat_suppressed"] = False

            logger.info(
                "Chunk %s | phase1=%.3f chat=%.3f final=%.3f",
                entry.get("file", "unknown"),
                base,
                chat_boost,
                entry["final_score"],
            )

        with open(chunks_path, "w", encoding="utf-8") as f:
            json.dump(chunks, f, indent=2)

        logger.info("Chat boost applied successfully")

    except Exception as e:
        logger.exception("Chat boost failed")
        raise



def chat_is_significant(start, end, mps_by_sec):
    total_msgs = 0
    active_secs = 0

    for sec in range(start, end + 1):
        count = mps_by_sec.get(sec, 0)
        if count > 0:
            active_secs += 1
            total_msgs += count

    return (
        total_msgs >= MIN_CHAT_MESSAGES_PER_CHUNK
        and active_secs >= MIN_CHAT_ACTIVE_SECONDS_PER_CHUNK
    )