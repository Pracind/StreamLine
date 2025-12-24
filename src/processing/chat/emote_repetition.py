import json
from collections import Counter, defaultdict
from pathlib import Path

from infra.config import DATA_DIR, CHAT_METRICS_DIR


def detect_repeated_emotes(logger) -> Path:
    """
    Detects repeated emotes per second.
    """

    # We need per-message emote tokens, so re-read normalized chat
    input_chat = DATA_DIR / "chat" / "normalized.json"
    output_path = CHAT_METRICS_DIR / "repeated_emotes.json"

    if not input_chat.exists():
        raise FileNotFoundError(f"Normalized chat not found: {input_chat}")

    if output_path.exists():
        logger.info("Using cached repeated-emote metrics")
        return output_path

    logger.info("Detecting repeated emotes")

    with open(input_chat, "r", encoding="utf-8") as f:
        data = json.load(f)

    emotes_by_second = defaultdict(list)

    for msg in data["messages"]:
        sec = int(msg["vod_time_sec"])
        tokens = msg.get("emote_tokens", [])
        emotes_by_second[sec].extend(tokens)

    timeline = []

    for sec in sorted(emotes_by_second.keys()):
        tokens = emotes_by_second[sec]

        if not tokens:
            continue

        counts = Counter(tokens)
        most_common_emote, repeat_count = counts.most_common(1)[0]

        timeline.append(
            {
                "second": sec,
                "total_emotes": len(tokens),
                "unique_emotes": len(counts),
                "top_emote": most_common_emote,
                "top_emote_count": repeat_count,
            }
        )

    output = {
        "vod_id": data.get("vod_id"),
        "timeline": timeline,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False)

    logger.info(
        "Repeated-emote detection complete: %d seconds",
        len(timeline),
    )

    return output_path
