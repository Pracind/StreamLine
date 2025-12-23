import json
from pathlib import Path
from typing import Dict, Any

from infra.config import (
    TWITCH_CHAT_RAW_DIR,
    TWITCH_CHAT_NORMALIZED_DIR,
)


def normalize_chat_timestamps(vod_id: str, logger) -> Path:
    """
    Converts Twitch chat timestamps to seconds-from-VOD-start.
    Writes normalized chat JSON.
    """

    raw_path = TWITCH_CHAT_RAW_DIR / f"{vod_id}.json"
    out_path = TWITCH_CHAT_NORMALIZED_DIR / f"{vod_id}.json"

    if not raw_path.exists():
        raise FileNotFoundError(f"Raw chat file not found: {raw_path}")

    if out_path.exists():
        logger.info("Using cached normalized chat timestamps")
        return out_path

    logger.info("Normalizing chat timestamps")

    with open(raw_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    comments = raw.get("comments", [])
    normalized_comments = []

    dropped = 0

    for msg in comments:
        offset = msg.get("content_offset_seconds")

        if offset is None:
            dropped += 1
            continue

        try:
            vod_time = float(offset)
        except (TypeError, ValueError):
            dropped += 1
            continue

        normalized_msg: Dict[str, Any] = {
            "vod_time_sec": vod_time,
            "message": msg.get("message"),
            "commenter": msg.get("commenter"),
            "emotes": msg.get("message", {}).get("emotes", []),
            "raw": msg,  # preserve full original message
        }

        normalized_comments.append(normalized_msg)

    output = {
        "vod_id": raw.get("video", {}).get("id"),
        "message_count": len(normalized_comments),
        "dropped_messages": dropped,
        "messages": normalized_comments,
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False)

    logger.info(
        "Chat timestamp normalization complete: %d messages (%d dropped)",
        len(normalized_comments),
        dropped,
    )

    return out_path
