import json
from pathlib import Path

from infra.config import DATA_DIR, TWITCH_CHAT_CLEAN_DIR


def export_final_chat(vod_id: str, logger) -> Path:
    """
    Exports the final, canonical normalized chat file.
    This is the ONLY chat file used by metrics and scoring.
    """

    input_path = TWITCH_CHAT_CLEAN_DIR / f"{vod_id}.json"
    output_dir = DATA_DIR / "chat"
    output_path = output_dir / "normalized.json"

    output_dir.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        raise FileNotFoundError(f"Clean chat file not found: {input_path}")

    logger.info("Exporting final normalized chat to %s", output_path)

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    final_payload = {
        "vod_id": vod_id,
        "message_count": len(data.get("messages", [])),
        "messages": data.get("messages", []),
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_payload, f, ensure_ascii=False)

    logger.info(
        "Final chat export complete (%d messages)",
        final_payload["message_count"],
    )

    return output_path
