import json
import math
from collections import defaultdict
from pathlib import Path

from infra.config import DATA_DIR, CHAT_METRICS_DIR
from processing.chat.chat_keywords import load_chat_keywords


def compute_chat_keyword_hits(logger) -> Path:
    """
    Counts chat keyword / phrase hits per second.
    """

    input_path = DATA_DIR / "chat" / "normalized.json"
    output_path = CHAT_METRICS_DIR / "chat_keyword_hits.json"

    if not input_path.exists():
        raise FileNotFoundError(f"Normalized chat not found: {input_path}")

    if output_path.exists():
        logger.info("Using cached chat keyword hits")
        return output_path

    logger.info("Computing chat keyword hits per second")

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    keywords = load_chat_keywords()

    hits_per_sec = defaultdict(int)
    messages_per_sec = defaultdict(int)
    keywords_per_sec = defaultdict(set)

    for msg in data["messages"]:
        t = msg.get("vod_time_sec")
        text = msg.get("text", "")

        if t is None or not text:
            continue

        sec = int(math.floor(t))
        messages_per_sec[sec] += 1

        for kw in keywords:
            if kw in text:
                hits_per_sec[sec] += 1
                keywords_per_sec[sec].add(kw)

    timeline = []
    all_seconds = sorted(
        set(messages_per_sec.keys()) | set(hits_per_sec.keys())
    )

    for sec in all_seconds:
        timeline.append(
            {
                "second": sec,
                "messages": messages_per_sec.get(sec, 0),
                "keyword_hits": hits_per_sec.get(sec, 0),
                "keywords": sorted(keywords_per_sec.get(sec, [])),
            }
        )

    output = {
        "vod_id": data.get("vod_id"),
        "timeline": timeline,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False)

    logger.info(
        "Chat keyword hits computed: %d seconds",
        len(timeline),
    )

    return output_path
