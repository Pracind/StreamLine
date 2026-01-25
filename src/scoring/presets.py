"""
Scoring preset persistence utilities.

This module allows saving and loading groups of scoring-related
configuration values as named presets, enabling reproducible
tuning and experimentation.
"""

import json
from infra.config import PRESETS_DIR
import infra.config as config


def save_preset(name: str):
    """
    Save the current scoring configuration as a named preset.

    The preset captures a snapshot of relevant runtime configuration
    values and persists them as a JSON file under the presets directory.

    Args:
        name: Name of the preset (used as the filename).
    """
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
    """
    Load a named scoring preset and apply it to the runtime configuration.

    This function mutates global configuration values in infra.config
    to match those stored in the preset.

    Args:
        name: Name of the preset to load (without file extension).

    Returns:
        The loaded preset dictionary.

    Raises:
        FileNotFoundError: If the requested preset does not exist.
    """
    path = PRESETS_DIR / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(path)

    preset = json.loads(path.read_text())

    # Apply preset values to runtime configuration
    config.ENABLE_CHAT_INFLUENCE = preset["enable_chat_influence"]
    config.CHAT_WEIGHT = preset["chat_weight"]

    config.AUDIO_WEIGHT = preset["audio_weight"]
    config.TEXT_WEIGHT = preset["text_weight"]

    config.HIGHLIGHT_THRESHOLD = preset["highlight_threshold"]

    config.CHAT_ONLY_MIN_SCORE = preset["chat_only_min_score"]
    config.MIN_CHAT_MESSAGES_PER_CHUNK = preset["min_chat_messages_per_chunk"]
    config.MIN_CHAT_ACTIVE_SECONDS_PER_CHUNK = preset["min_chat_active_seconds_per_chunk"]

    return preset
