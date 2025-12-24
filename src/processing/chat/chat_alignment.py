import json
from pathlib import Path

from infra.config import CHAT_METRICS_DIR, CHAT_TO_VIDEO_OFFSET_SECONDS


def align_chat_to_video(logger, video_duration_seconds: int) -> Path:
    """
    Aligns chat score timeline to video timeline using a fixed offset.
    """

    input_path = CHAT_METRICS_DIR / "chat_scores.json"
    output_path = CHAT_METRICS_DIR / "chat_scores_aligned.json"

    if not input_path.exists():
        raise FileNotFoundError(f"Chat scores not found: {input_path}")

    if output_path.exists():
        logger.info("Using cached aligned chat scores")
        return output_path

    logger.info(
        "Aligning chat timeline to video (offset=%ds)",
        CHAT_TO_VIDEO_OFFSET_SECONDS,
    )

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    aligned = []

    for item in data["timeline"]:
        chat_sec = item["second"]
        video_sec = chat_sec - CHAT_TO_VIDEO_OFFSET_SECONDS

        if video_sec < 0:
            continue

        if video_sec >= video_duration_seconds:
            continue

        aligned.append(
            {
                "video_second": video_sec,
                "chat_second": chat_sec,
                "score": item["score"],

                # explainability preserved
                "activity": item.get("activity", 0.0),
                "emote": item.get("emote", 0.0),
                "keyword": item.get("keyword", 0.0),
            }
        )

    output = {
        "signal_type": "chat",
        "offset_seconds": CHAT_TO_VIDEO_OFFSET_SECONDS,
        "timeline": aligned,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False)

    logger.info(
        "Chat-video alignment complete: %d seconds",
        len(aligned),
    )

    return output_path
