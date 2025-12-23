import json
from pathlib import Path

from infra.config import (
    TWITCH_CHAT_NORMALIZED_DIR,
    TWITCH_CHAT_TEXT_DIR,
)


def normalize_chat_text(vod_id: str, logger) -> Path:
    """
    Normalizes chat message text:
    - lowercase
    - trim whitespace
    """

    in_path = TWITCH_CHAT_NORMALIZED_DIR / f"{vod_id}.json"
    out_path = TWITCH_CHAT_TEXT_DIR / f"{vod_id}.json"

    if not in_path.exists():
        raise FileNotFoundError(f"Normalized chat file not found: {in_path}")

    if out_path.exists():
        logger.info("Using cached normalized chat text")
        return out_path

    logger.info("Normalizing chat message text")

    with open(in_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    messages = data["messages"]
    normalized = []

    for msg in messages:
        raw_msg = msg.get("message", {})
        body = raw_msg.get("body", "")

        if not isinstance(body, str):
            body = ""

        text_norm = body.strip().lower()

        new_msg = {
            **msg,
            "text_raw": body,
            "text_norm": text_norm,
        }

        normalized.append(new_msg)

    output = {
        **data,
        "messages": normalized,
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False)

    logger.info(
        "Chat text normalization complete: %d messages",
        len(normalized),
    )

    return out_path
