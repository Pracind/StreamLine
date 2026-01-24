"""
Apply chat-based score boosts to chunk-level scores.

This module integrates aligned chat activity signals into the final
chunk scores, subject to significance gating and configurable caps.
"""

import json
import infra.config as config

from infra.config import CHAT_WEIGHT, CHAT_BOOST_MAX


def apply_chat_boost_to_chunks(logger, chat_weight: float):
    """
    Apply chat-derived score boosts to chunk metadata.

    This function:
    - Loads per-second chat metrics and aligned chat scores
    - Gates boosts based on minimum chat activity thresholds
    - Applies a capped, weighted boost to qualifying chunks
    - Updates final scores in-place within chunks.json

    Args:
        logger: Logger instance for progress and error reporting.
        chat_weight: Scaling factor applied to chat-derived boost values.
    """
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

        # Load chat activity metrics (messages per second)
        with open(mps_path, "r", encoding="utf-8") as f:
            mps_data = json.load(f)

        mps_by_sec = {
            int(item["second"]): int(item["messages"])
            for item in mps_data.get("timeline", [])
        }

        # Load aligned chat score timeline
        with open(chat_scores_path, "r", encoding="utf-8") as f:
            chat_data = json.load(f)

        chat_by_sec = {
            int(item["video_second"]): float(item["score"])
            for item in chat_data.get("timeline", [])
        }

        # Load chunk metadata
        with open(chunks_path, "r", encoding="utf-8") as f:
            chunks = json.load(f)

        for entry in chunks:
            start = int(entry["start_time"])
            end = int(entry["end_time"])

            # Base score prior to chat influence
            base = float(entry.get("phase1_score", entry.get("final_score", 0.0)))

            # Gate chat influence based on minimum activity
            if not chat_is_significant(start, end, mps_by_sec):
                entry["chat_boost"] = 0.0
                entry["final_score"] = base
                entry["chat_suppressed"] = True
                continue

            # Compute maximum chat score across the chunk interval
            chat_boost = 0.0
            for sec in range(start, end + 1):
                chat_boost = max(chat_boost, chat_by_sec.get(sec, 0.0))

            # Apply weighting and cap the boost
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

        # Persist updated chunk scores
        with open(chunks_path, "w", encoding="utf-8") as f:
            json.dump(chunks, f, indent=2)

        logger.info("Chat boost applied successfully")

    except Exception as e:
        logger.exception("Chat boost failed")
        raise


def chat_is_significant(start, end, mps_by_sec):
    """
    Determine whether chat activity is significant for a time window.

    Significance requires both:
    - A minimum total number of messages
    - A minimum number of active seconds with chat messages

    Args:
        start: Start time (seconds).
        end: End time (seconds).
        mps_by_sec: Mapping of second → message count.

    Returns:
        True if chat activity meets significance thresholds, else False.
    """
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
