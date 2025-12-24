import json
import math
from collections import defaultdict
from pathlib import Path

from infra.config import DATA_DIR, CHAT_METRICS_DIR


def compute_messages_per_second(logger) -> Path:
    """
    Computes messages-per-second (MPS) from normalized chat.
    """

    input_path = DATA_DIR / "chat" / "normalized.json"
    output_path = CHAT_METRICS_DIR / "messages_per_second.json"

    if not input_path.exists():
        raise FileNotFoundError(f"Normalized chat not found: {input_path}")

    if output_path.exists():
        logger.info("Using cached messages-per-second metrics")
        return output_path

    logger.info("Computing messages per second")

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    counts = defaultdict(int)

    for msg in data["messages"]:
        t = msg.get("vod_time_sec")
        if t is None:
            continue

        sec = int(math.floor(t))
        counts[sec] += 1

    # Convert to sorted list for easier downstream use
    timeline = [
        {"second": sec, "messages": counts[sec]}
        for sec in sorted(counts.keys())
    ]

    output = {
        "vod_id": data.get("vod_id"),
        "total_messages": len(data.get("messages", [])),
        "timeline": timeline,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False)

    logger.info(
        "Messages-per-second computed: %d seconds",
        len(timeline),
    )

    return output_path
