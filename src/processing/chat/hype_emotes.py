import json
from infra.config import HYPE_EMOTES_PATH


def load_hype_emotes() -> set[str]:
    """
    Loads configured hype emotes.
    Returns a flat set of emote names.
    """

    if not HYPE_EMOTES_PATH.exists():
        raise FileNotFoundError(f"Hype emotes config missing: {HYPE_EMOTES_PATH}")

    with open(HYPE_EMOTES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    emotes = set()
    for group in data.values():
        emotes.update(group)

    return emotes
