import json
from infra.config import CHAT_KEYWORDS_PATH


def load_chat_keywords() -> set[str]:
    """
    Loads configured chat keywords / phrases.
    Returns a flat set of lowercase strings.
    """

    if not CHAT_KEYWORDS_PATH.exists():
        raise FileNotFoundError(f"Chat keywords config missing: {CHAT_KEYWORDS_PATH}")

    with open(CHAT_KEYWORDS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    keywords = set()
    for group in data.values():
        for kw in group:
            keywords.add(kw.lower())

    return keywords
