import json
from pathlib import Path

from infra.config import (
    CHAT_METRICS_DIR,
    CHAT_SPIKE_RATIO_THRESHOLD,
    CHAT_MIN_BASELINE,
)


def _log_debug_metrics(baseline_timeline, spikes, logger):
    """
    Logs high-level diagnostic metrics for chat activity.
    """

    mps_values = [x["messages"] for x in baseline_timeline]
    baseline_values = [x["baseline"] for x in baseline_timeline if x["baseline"] > 0]

    max_mps = max(mps_values) if mps_values else 0
    avg_mps = (
        sum(v for v in mps_values if v > 0) / max(1, len([v for v in mps_values if v > 0]))
    )

    max_baseline = max(baseline_values) if baseline_values else 0
    avg_baseline = (
        sum(baseline_values) / max(1, len(baseline_values))
    )

    max_spike = max(
        (s["magnitude"] for s in spikes),
        default=0,
    )

    logger.info("=== Chat Metrics Summary ===")
    logger.info("Max MPS: %.2f", max_mps)
    logger.info("Avg MPS (non-zero): %.3f", avg_mps)
    logger.info("Max baseline: %.3f", max_baseline)
    logger.info("Avg baseline: %.3f", avg_baseline)
    logger.info("Spike count: %d", len(spikes))
    logger.info("Max spike magnitude: %.2f", max_spike)


def detect_chat_spikes(logger) -> Path:
    """
    Detects chat activity spikes using a ratio over rolling baseline.
    """

    input_path = CHAT_METRICS_DIR / "rolling_baseline.json"
    output_path = CHAT_METRICS_DIR / "chat_spikes.json"

    if not input_path.exists():
        raise FileNotFoundError(f"Baseline file not found: {input_path}")

    if output_path.exists():
        logger.info("Using cached chat spikes")
        return output_path

    logger.info(
        "Detecting chat spikes (ratio>=%.2f, min_baseline>=%.2f)",
        CHAT_SPIKE_RATIO_THRESHOLD,
        CHAT_MIN_BASELINE,
    )

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    spikes = []

    for item in data["timeline"]:
        sec = item["second"]
        mps = item["messages"]
        baseline = item["baseline"]

        if baseline < CHAT_MIN_BASELINE:
            continue

        ratio = mps / baseline if baseline > 0 else 0.0

        if baseline > 0:
            logger.debug(
                "sec=%d mps=%.2f baseline=%.2f ratio=%.2f",
                sec,
                mps,
                baseline,
                ratio,
            )

        if ratio >= CHAT_SPIKE_RATIO_THRESHOLD:
            spikes.append(
                {
                    "timestamp_sec": sec,
                    "magnitude": ratio,
                    "messages_per_second": mps,
                    "baseline": baseline,
                }
            )

    _log_debug_metrics(data["timeline"], spikes, logger)

    output = {
        "vod_id": data.get("vod_id"),
        "threshold_ratio": CHAT_SPIKE_RATIO_THRESHOLD,
        "min_baseline": CHAT_MIN_BASELINE,
        "spike_count": len(spikes),
        "spikes": spikes,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False)

    logger.info("Chat spike detection complete: %d spikes", len(spikes))

    return output_path
