import json
from pathlib import Path

from infra.config import CHAT_METRICS_DIR


def export_final_chat_scores(logger) -> Path:
    """
    Exports final smoothed chat scores under canonical filename.
    """

    input_path = CHAT_METRICS_DIR / "chat_score_smoothed.json"
    output_path = CHAT_METRICS_DIR / "chat_scores.json"

    if not input_path.exists():
        raise FileNotFoundError(
            f"Smoothed chat score not found: {input_path}"
        )

    # Always overwrite to guarantee freshness
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

    logger.info(
        "Final chat scores exported: %s",
        output_path,
    )

    return output_path
