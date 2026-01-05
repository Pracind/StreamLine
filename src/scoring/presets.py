import json
from infra.config import PRESETS_DIR
import infra.config as config

def save_preset(name: str):
    preset = {
        "name": name,
        "version": 1,

        "enable_chat_influence": config.ENABLE_CHAT_INFLUENCE,
        "chat_weight": config.CHAT_WEIGHT,

        "audio_weight": config.AUDIO_WEIGHT,
        "text_weight": config.TEXT_WEIGHT,

        "highlight_threshold": config.HIGHLIGHT_THRESHOLD,

        "chat_only_min_score": config.CHAT_ONLY_MIN_SCORE,
        "min_chat_messages_per_chunk": config.MIN_CHAT_MESSAGES_PER_CHUNK,
        "min_chat_active_seconds_per_chunk": config.MIN_CHAT_ACTIVE_SECONDS_PER_CHUNK,
    }

    path = PRESETS_DIR / f"{name}.json"
    path.write_text(json.dumps(preset, indent=2))


def load_preset(name: str):
    path = PRESETS_DIR / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(path)

    preset = json.loads(path.read_text())

    # Apply to runtime config
    config.ENABLE_CHAT_INFLUENCE = preset["enable_chat_influence"]
    config.CHAT_WEIGHT = preset["chat_weight"]

    config.AUDIO_WEIGHT = preset["audio_weight"]
    config.TEXT_WEIGHT = preset["text_weight"]

    config.HIGHLIGHT_THRESHOLD = preset["highlight_threshold"]

    config.CHAT_ONLY_MIN_SCORE = preset["chat_only_min_score"]
    config.MIN_CHAT_MESSAGES_PER_CHUNK = preset["min_chat_messages_per_chunk"]
    config.MIN_CHAT_ACTIVE_SECONDS_PER_CHUNK = preset["min_chat_active_seconds_per_chunk"]

    return preset