import json
import infra.config as config

from infra.config import CHAT_WEIGHT, CHAT_BOOST_MAX


def apply_chat_boost_to_chunks(logger, chat_weight: float):
    try:
        if not config.ENABLE_CHAT_INFLUENCE:
            logger.info("Chat influence disabled — skipping chat boost")
            return

        mps_path = config.CHAT_METRICS_DIR / "messages_per_second.json"
        chat_scores_path = config.CHAT_METRICS_DIR / "chat_scores_aligned.json"
        chunks_path = config.CHUNKS_DIR / "chunks.json"

        if not mps_path.exists():
            logger.warning("messages_per_second.json not found — skipping chat boost")
            return

        if not chat_scores_path.exists():
            logger.warning("chat_scores_aligned.json not found — skipping chat boost")
            return

        if not chunks_path.exists():
            raise RuntimeError("chunks.json not found")

        logger.info("Applying chat boost with weight = %.2f", chat_weight)

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

            weighted_boost = min(chat_boost * chat_weight, CHAT_BOOST_MAX)

            entry["chat_boost"] = weighted_boost
            entry["final_score"] = min(1.0, base + weighted_boost)
            entry["chat_suppressed"] = False

            logger.info(
                "Chunk %s | phase1=%.3f chat=%.3f weight=%.2f final=%.3f",
                entry.get("file", "unknown"),
                base,
                weighted_boost,
                chat_weight,
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
        total_msgs >= config.MIN_CHAT_MESSAGES_PER_CHUNK
        and active_secs >= config.MIN_CHAT_ACTIVE_SECONDS_PER_CHUNK
    )