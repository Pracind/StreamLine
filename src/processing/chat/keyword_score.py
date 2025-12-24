import json
import math
from pathlib import Path

from infra.config import CHAT_METRICS_DIR, KEYWORD_SCORE_SCALE


def compute_chat_keyword_score(logger) -> Path:
    """
    Computes normalized chat keyword score per second in [0, 1].
    """

    input_path = CHAT_METRICS_DIR / "chat_keyword_hits.json"
    output_path = CHAT_METRICS_DIR / "chat_keyword_score.json"

    if not input_path.exists():
        raise FileNotFoundError(f"Keyword hits not found: {input_path}")

    if output_path.exists():
        logger.info("Using cached chat keyword score")
        return output_path

    logger.info("Normalizing chat keyword score")

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    timeline = []

    for item in data["timeline"]:
        messages = item["messages"]
        hits = item["keyword_hits"]

        if messages == 0 or hits == 0:
            continue

        density = hits / messages
        score = math.tanh(density / KEYWORD_SCORE_SCALE)

        timeline.append(
            {
                "second": item["second"],
                "score": score,

                # metadata for explainability
                "keyword_hits": hits,
                "messages": messages,
                "keywords": item["keywords"],
                "signal": "keyword",
            }
        )

    output = {
        "signal_type": "keyword",
        "scale": KEYWORD_SCORE_SCALE,
        "timeline": timeline,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False)

    logger.info(
        "Chat keyword score computed: %d seconds",
        len(timeline),
    )

    return output_path
