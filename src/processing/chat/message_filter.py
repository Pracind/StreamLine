import json
import re
from pathlib import Path

from infra.config import (
    TWITCH_CHAT_EMOTES_DIR,
    TWITCH_CHAT_CLEAN_DIR,
)

# Very conservative spam patterns
SYSTEM_MESSAGE_PATTERNS = [
    re.compile(r"has (subscribed|gifted|redeemed)", re.I),
    re.compile(r"^welcome to the chat", re.I),
]

PURE_PUNCTUATION_RE = re.compile(r"^[\W_]+$")


def filter_chat_messages(vod_id: str, logger) -> Path:
    """
    Filters empty and obvious spam/system chat messages.
    """

    in_path = TWITCH_CHAT_EMOTES_DIR / f"{vod_id}.json"
    out_path = TWITCH_CHAT_CLEAN_DIR / f"{vod_id}.json"

    if not in_path.exists():
        raise FileNotFoundError(f"Emote chat file not found: {in_path}")

    if out_path.exists():
        logger.info("Using cached cleaned chat")
        return out_path

    logger.info("Filtering empty / spam chat messages")

    with open(in_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    kept = []
    dropped = 0

    for msg in data["messages"]:
        text = (msg.get("text_userless") or "").strip()
        emote_count = msg.get("emote_count", 0)

        # 1) Empty text and no emotes
        if not text and emote_count == 0:
            dropped += 1
            continue

        # 2) Pure punctuation and no emotes
        if PURE_PUNCTUATION_RE.match(text) and emote_count == 0:
            dropped += 1
            continue

        # 3) Very short noise without emotes
        if len(text) < 2 and emote_count == 0:
            dropped += 1
            continue

        # 4) System / bot messages
        if any(p.search(text) for p in SYSTEM_MESSAGE_PATTERNS):
            dropped += 1
            continue

        kept.append(msg)

    output = {
        **data,
        "messages": kept,
        "filtered_out": dropped,
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False)

    logger.info(
        "Chat filtering complete: %d kept, %d dropped",
        len(kept),
        dropped,
    )

    return out_path
