import json
from collections import deque
from pathlib import Path

from infra.config import DATA_DIR, CHAT_METRICS_DIR, CHAT_BASELINE_WINDOW_SECONDS


def compute_rolling_baseline(logger) -> Path:
    """
    Computes rolling average baseline over messages-per-second.
    Uses a trailing window of CHAT_BASELINE_WINDOW_SECONDS.
    Missing seconds are treated as zero.
    """

    input_path = CHAT_METRICS_DIR / "messages_per_second.json"
    output_path = CHAT_METRICS_DIR / "rolling_baseline.json"

    if not input_path.exists():
        raise FileNotFoundError(f"MPS file not found: {input_path}")

    if output_path.exists():
        logger.info("Using cached rolling baseline")
        return output_path

    logger.info(
        "Computing rolling baseline (window=%ds)",
        CHAT_BASELINE_WINDOW_SECONDS,
    )

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    timeline = data["timeline"]

    # Build a dense timeline: second -> messages
    counts = {item["second"]: item["messages"] for item in timeline}
    if not counts:
        raise ValueError("Empty MPS timeline")

    min_sec = min(counts.keys())
    max_sec = max(counts.keys())

    window = deque()
    window_sum = 0.0

    baseline_timeline = []

    for sec in range(min_sec, max_sec + 1):
        val = counts.get(sec, 0)

        window.append(val)
        window_sum += val

        if len(window) > CHAT_BASELINE_WINDOW_SECONDS:
            window_sum -= window.popleft()

        baseline = window_sum / len(window)

        baseline_timeline.append(
            {
                "second": sec,
                "messages": val,
                "baseline": baseline,
            }
        )

    output = {
        "vod_id": data.get("vod_id"),
        "window_seconds": CHAT_BASELINE_WINDOW_SECONDS,
        "timeline": baseline_timeline,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False)

    logger.info(
        "Rolling baseline computed: %d seconds",
        len(baseline_timeline),
    )

    return output_path
