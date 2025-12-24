import json
import math
from collections import defaultdict
from pathlib import Path

from infra.config import DATA_DIR, CHAT_METRICS_DIR


def compute_emote_density_per_second(logger) -> Path:
    """
    Computes emote density per second from normalized chat.
    """

    input_path = DATA_DIR / "chat" / "normalized.json"
    output_path = CHAT_METRICS_DIR / "emote_density.json"

    if not input_path.exists():
        raise FileNotFoundError(f"Normalized chat not found: {input_path}")

    if output_path.exists():
        logger.info("Using cached emote density metrics")
        return output_path

    logger.info("Computing emote density per second")

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    emotes_per_sec = defaultdict(int)
    messages_per_sec = defaultdict(int)

    for msg in data["messages"]:
        t = msg.get("vod_time_sec")
        if t is None:
            continue

        sec = int(math.floor(t))

        emote_count = len(msg.get("emote_tokens", []))
        emotes_per_sec[sec] += emote_count

        messages_per_sec[sec] += 1

    timeline = []
    all_seconds = sorted(set(emotes_per_sec.keys()) | set(messages_per_sec.keys()))

    for sec in all_seconds:
        emotes = emotes_per_sec.get(sec, 0)
        msgs = messages_per_sec.get(sec, 0)

        timeline.append(
            {
                "second": sec,
                "emotes": emotes,
                "messages": msgs,
                "emotes_per_message": (emotes / msgs) if msgs > 0 else 0.0,
            }
        )

    output = {
        "vod_id": data.get("vod_id"),
        "timeline": timeline,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False)

    logger.info(
        "Emote density computed: %d seconds",
        len(timeline),
    )

    return output_path
