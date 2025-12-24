import json
import math
from pathlib import Path

from infra.config import CHAT_METRICS_DIR, DATA_DIR, EMOTE_SCORE_SCALE
from processing.chat.hype_emotes import load_hype_emotes


def compute_emote_score(logger) -> Path:
    """
    Computes normalized emote score per second in [0, 1].
    """

    density_path = CHAT_METRICS_DIR / "emote_density.json"
    repeat_path = CHAT_METRICS_DIR / "repeated_emotes.json"
    output_path = CHAT_METRICS_DIR / "emote_score.json"

    if not density_path.exists() or not repeat_path.exists():
        raise FileNotFoundError("Required emote metric files missing")

    if output_path.exists():
        logger.info("Using cached emote score")
        return output_path

    logger.info("Normalizing emote score")

    with open(density_path, "r", encoding="utf-8") as f:
        density = json.load(f)["timeline"]

    with open(repeat_path, "r", encoding="utf-8") as f:
        repeats = json.load(f)["timeline"]

    hype_emotes = load_hype_emotes()

    repeat_by_sec = {x["second"]: x for x in repeats}

    timeline = []

    for item in density:
        sec = item["second"]
        total_emotes = item["emotes"]

        if total_emotes == 0:
            continue

        rep = repeat_by_sec.get(sec)
        if not rep:
            continue

        top_emote = rep["top_emote"]
        top_count = rep["top_emote_count"]

        hype_count = top_count if top_emote in hype_emotes else 0
        repeat_strength = top_count / total_emotes

        raw = hype_count * repeat_strength
        score = math.tanh(raw / EMOTE_SCORE_SCALE)

        timeline.append(
            {
                "second": sec,
                "score": score,

                # scoring inputs
                "top_emote": top_emote,
                "top_emote_count": top_count,
                "total_emotes": total_emotes,
                "repeat_strength": repeat_strength,
                "hype_emote_count": hype_count,

                # explanation helper
                "signal": "emote",
            }
        )

    output = {
        "signal_type": "emote",
        "scale": EMOTE_SCORE_SCALE,
        "timeline": timeline,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False)

    logger.info("Emote score computed: %d seconds", len(timeline))

    return output_path
