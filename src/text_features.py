import json
from pathlib import Path

from src.config import DATA_DIR

KEYWORDS_PATH = DATA_DIR / "keywords.json"
TRANSCRIPTS_DIR = DATA_DIR / "transcripts"
TEXT_FEATURES_PATH = DATA_DIR / "text_features.json"


def load_keywords():
    if not KEYWORDS_PATH.exists():
        raise RuntimeError("keywords.json not found")

    with open(KEYWORDS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def count_keywords_in_text(text, keywords_by_category):
    text_lower = text.lower()

    counts = {}
    for category, phrases in keywords_by_category.items():
        count = 0
        for phrase in phrases:
            phrase_lower = phrase.lower()
            count += text_lower.count(phrase_lower)
        counts[category] = count

    return counts


def count_keyword_hits_per_chunk():
    all_keywords = load_keywords()
    keywords_by_category = {
        k: v for k, v in all_keywords.items() if k != "sentiment"
    }
    sentiment_config = all_keywords.get("sentiment", {})

    transcripts = sorted(TRANSCRIPTS_DIR.glob("chunk_*.json"))

    if not transcripts:
        raise RuntimeError("No transcripts found for keyword analysis.")

    all_features = {}

    for transcript_path in transcripts:
        with open(transcript_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        text = data.get("text", "")

        counts = count_keywords_in_text(text, keywords_by_category)
        sentiment = compute_sentiment(text, sentiment_config)

        raw_text_score = sum(counts.values()) + sentiment["sentiment_raw"]

        all_features[transcript_path.stem] = {
            "keyword_counts": counts,
            "total_keywords": sum(counts.values()),
            "sentiment": sentiment,
            "raw_text_score": raw_text_score,
        }

    all_features = normalize_text_scores(all_features)

    with open(TEXT_FEATURES_PATH, "w", encoding="utf-8") as f:
        json.dump(all_features, f, indent=2)

    return all_features


def compute_sentiment(text, sentiment_config):
    text_lower = text.lower()

    positive = sentiment_config.get("positive", [])
    negative = sentiment_config.get("negative", [])

    pos_hits = sum(text_lower.count(p.lower()) for p in positive)
    neg_hits = sum(text_lower.count(n.lower()) for n in negative)

    return {
        "positive_hits": pos_hits,
        "negative_hits": neg_hits,
        "sentiment_raw": pos_hits - neg_hits,
    }


def normalize_text_scores(all_features):
    raw_scores = [
        data["raw_text_score"]
        for data in all_features.values()
    ]

    if not raw_scores:
        return all_features

    min_score = min(raw_scores)
    max_score = max(raw_scores)

    for data in all_features.values():
        if max_score == min_score:
            data["text_score"] = 0.0
        else:
            data["text_score"] = (
                (data["raw_text_score"] - min_score)
                / (max_score - min_score)
            )

    return all_features