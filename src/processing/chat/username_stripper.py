import json
import re
from pathlib import Path

from infra.config import (
    TWITCH_CHAT_TEXT_DIR,
    TWITCH_CHAT_USERLESS_DIR,
)

# Patterns to strip username prefixes
USERNAME_PREFIX_PATTERNS = [
    re.compile(r"^[^:\s]{1,25}:\s+"),   # username: message
    re.compile(r"^@[^:\s]{1,25}\s+"),   # @username message
]


def strip_usernames(vod_id: str, logger) -> Path:
    """
    Removes usernames and IDs from chat messages.
    """

    in_path = TWITCH_CHAT_TEXT_DIR / f"{vod_id}.json"
    out_path = TWITCH_CHAT_USERLESS_DIR / f"{vod_id}.json"

    if not in_path.exists():
        raise FileNotFoundError(f"Normalized text file not found: {in_path}")

    if out_path.exists():
        logger.info("Using cached userless chat")
        return out_path

    logger.info("Stripping usernames from chat messages")

    with open(in_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    cleaned = []

    for msg in data["messages"]:
        text = msg.get("text_norm", "")

        # Strip common username prefixes
        for pattern in USERNAME_PREFIX_PATTERNS:
            text = pattern.sub("", text)

        new_msg = {
            **msg,
            "text_userless": text,
        }

        # Remove structured identity
        new_msg.pop("commenter", None)

        cleaned.append(new_msg)

    output = {
        **data,
        "messages": cleaned,
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False)

    logger.info(
        "Username stripping complete: %d messages",
        len(cleaned),
    )

    return out_path
