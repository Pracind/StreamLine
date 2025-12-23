import json
from pathlib import Path

from infra.config import (
    TWITCH_CHAT_USERLESS_DIR,
    TWITCH_CHAT_EMOTES_DIR,
)


def extract_emotes(vod_id: str, logger) -> Path:
    """
    Extracts emotes as normalized token lists per message.
    """

    in_path = TWITCH_CHAT_USERLESS_DIR / f"{vod_id}.json"
    out_path = TWITCH_CHAT_EMOTES_DIR / f"{vod_id}.json"

    if not in_path.exists():
        raise FileNotFoundError(f"Userless chat file not found: {in_path}")

    if out_path.exists():
        logger.info("Using cached emote-extracted chat")
        return out_path

    logger.info("Extracting emotes from chat messages")

    with open(in_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    messages_out = []

    for msg in data["messages"]:
        raw = msg.get("raw", {})
        message = raw.get("message", {})

        emotes = message.get("emotes", []) or []

        # Normalize emote tokens
        tokens = []
        for e in emotes:
            name = e.get("name")
            if name:
                tokens.append(name)

        new_msg = {
            **msg,
            "emote_tokens": tokens,
            "emote_count": len(tokens),
        }

        messages_out.append(new_msg)

    output = {
        **data,
        "messages": messages_out,
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False)

    logger.info(
        "Emote extraction complete: %d messages",
        len(messages_out),
    )

    return out_path
