import json
from collections import defaultdict
from pathlib import Path

from infra.config import (
    CHAT_METRICS_DIR,
    CHAT_ACTIVITY_WEIGHT,
    CHAT_EMOTE_WEIGHT,
    CHAT_KEYWORD_WEIGHT,
)


def compute_chat_score(logger) -> Path:
    """
    Aggregates chat activity, emote score, and keyword score
    into a single per-second chat score.
    """

    spike_path = CHAT_METRICS_DIR / "chat_spikes.json"
    emote_path = CHAT_METRICS_DIR / "emote_score.json"
    keyword_path = CHAT_METRICS_DIR / "chat_keyword_score.json"
    output_path = CHAT_METRICS_DIR / "chat_score.json"

    if output_path.exists():
        logger.info("Using cached chat score")
        return output_path

    logger.info("Aggregating chat score")

    # ─── Load inputs ────────────────────────────────

    activity_by_sec = defaultdict(float)
    if spike_path.exists():
        with open(spike_path, "r", encoding="utf-8") as f:
            spikes = json.load(f)["spikes"]
        for s in spikes:
            activity_by_sec[s["timestamp_sec"]] = min(1.0, s["magnitude"] / 3.0)
            # magnitude normalization heuristic (Phase 2)

    with open(emote_path, "r", encoding="utf-8") as f:
        emotes = json.load(f)["timeline"]
    emote_by_sec = {e["second"]: e["score"] for e in emotes}

    with open(keyword_path, "r", encoding="utf-8") as f:
        keywords = json.load(f)["timeline"]
    keyword_by_sec = {k["second"]: k["score"] for k in keywords}

    all_seconds = sorted(
        set(activity_by_sec.keys())
        | set(emote_by_sec.keys())
        | set(keyword_by_sec.keys())
    )

    timeline = []

    for sec in all_seconds:
        activity = activity_by_sec.get(sec, 0.0)
        emote = emote_by_sec.get(sec, 0.0)
        keyword = keyword_by_sec.get(sec, 0.0)

        score = (
            CHAT_ACTIVITY_WEIGHT * activity
            + CHAT_EMOTE_WEIGHT * emote
            + CHAT_KEYWORD_WEIGHT * keyword
        )

        timeline.append(
            {
                "second": sec,
                "score": score,
                "activity": activity,
                "emote": emote,
                "keyword": keyword,
            }
        )

    output = {
        "signal_type": "chat",
        "weights": {
            "activity": CHAT_ACTIVITY_WEIGHT,
            "emote": CHAT_EMOTE_WEIGHT,
            "keyword": CHAT_KEYWORD_WEIGHT,
        },
        "timeline": timeline,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False)

    logger.info("Chat score aggregated: %d seconds", len(timeline))

    return output_path
