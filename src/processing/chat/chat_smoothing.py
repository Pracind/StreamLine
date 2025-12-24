import json
from collections import deque
from pathlib import Path

from infra.config import CHAT_METRICS_DIR, CHAT_SMOOTHING_WINDOW_SECONDS


def smooth_chat_score(logger) -> Path:
    """
    Applies rolling average smoothing to final chat score.
    """

    input_path = CHAT_METRICS_DIR / "chat_score.json"
    output_path = CHAT_METRICS_DIR / "chat_score_smoothed.json"

    if not input_path.exists():
        raise FileNotFoundError(f"Chat score not found: {input_path}")

    if output_path.exists():
        logger.info("Using cached smoothed chat score")
        return output_path

    logger.info(
        "Applying chat score smoothing (window=%ds)",
        CHAT_SMOOTHING_WINDOW_SECONDS,
    )

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    timeline = data["timeline"]

    # Ensure sorted by time
    timeline = sorted(timeline, key=lambda x: x["second"])

    window = deque()
    window_sum = 0.0

    smoothed_timeline = []

    for item in timeline:
        score = item["score"]

        window.append(score)
        window_sum += score

        if len(window) > CHAT_SMOOTHING_WINDOW_SECONDS:
            window_sum -= window.popleft()

        smoothed = window_sum / len(window)

        smoothed_timeline.append(
            {
                "second": item["second"],
                "score": smoothed,

                # retain explainability
                "raw_score": item["score"],
                "activity": item["activity"],
                "emote": item["emote"],
                "keyword": item["keyword"],
            }
        )

    output = {
        "signal_type": "chat",
        "smoothing_window_seconds": CHAT_SMOOTHING_WINDOW_SECONDS,
        "timeline": smoothed_timeline,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False)

    logger.info(
        "Chat score smoothing complete: %d seconds",
        len(smoothed_timeline),
    )

    return output_path
