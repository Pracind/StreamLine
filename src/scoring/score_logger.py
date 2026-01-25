"""
Score logging utilities for tuning and analysis.

This module exports chunk-level scoring data to a CSV file to enable
offline inspection, visualization, and threshold tuning.
"""

import csv
from pathlib import Path

from infra.config import CHUNKS_DIR, DATA_DIR


# Directory and file used for score logging output
LOGS_DIR = DATA_DIR / "logs"
LOG_FILE = LOGS_DIR / "score_log.csv"


def log_scores_for_tuning():
    """
    Export chunk scoring data to a CSV file for analysis.

    The CSV includes:
    - Chunk timing information
    - Audio and text scores
    - Final combined score
    - Highlight classification flag

    Returns:
        Number of chunks written to the log file.

    Raises:
        RuntimeError: If chunk metadata does not exist.
    """
    chunks_path = CHUNKS_DIR / "chunks.json"

    if not chunks_path.exists():
        raise RuntimeError("chunks.json not found")

    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    import json
    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    fieldnames = [
        "chunk_id",
        "start_time",
        "end_time",
        "audio_score",
        "text_score",
        "final_score",
        "is_highlight",
    ]

    # Write chunk scores to CSV for external tuning and inspection
    with open(LOG_FILE, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for entry in chunks:
            writer.writerow({
                "chunk_id": entry.get("chunk_id"),
                "start_time": entry.get("start_time"),
                "end_time": entry.get("end_time"),
                "audio_score": entry.get("audio_score"),
                "text_score": entry.get("text_score"),
                "final_score": entry.get("final_score"),
                "is_highlight": entry.get("is_highlight"),
            })

    return len(chunks)
