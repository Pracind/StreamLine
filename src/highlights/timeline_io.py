"""
Timeline load/save utilities with backward-compatible schema handling.

This module normalizes legacy highlight timeline formats into the current
v2 schema and provides a single persistence path for timeline artifacts.
"""

import json
from pathlib import Path
from typing import Dict, Any, List


# Current supported timeline schema version
SCHEMA_VERSION = 2


def _upgrade_v1_list_to_v2(raw_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Upgrade a legacy v1 timeline list into the v2 timeline schema.

    v1 timelines are bare lists of interval dictionaries without
    IDs, ordering, or editing metadata. This function injects
    stable IDs and default v2 fields.
    """
    timeline = []
    for idx, item in enumerate(raw_list):
        timeline.append({
            "id": f"hl_{idx:04d}",
            "start_time": float(item["start_time"]),
            "end_time": float(item["end_time"]),
            "chunk_ids": list(item.get("chunk_ids", [])),
            "enabled": True,
            "trim_start_offset": 0.0,
            "trim_end_offset": 0.0,
            "order_index": idx,
        })
    return {"schema_version": SCHEMA_VERSION, "timeline": timeline}


def load_timeline(path: Path) -> Dict[str, Any]:
    """
    Load a highlight timeline from disk and normalize it to v2 schema.

    Supported inputs:
    - v1: bare list of highlight intervals
    - v2: wrapped object with schema_version and timeline
    - Partial/legacy objects containing a timeline field

    Returns:
        A dictionary conforming to the v2 timeline schema.

    Raises:
        ValueError: If the file format cannot be interpreted.
    """
    if not path.exists():
        return {"schema_version": SCHEMA_VERSION, "timeline": []}

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # v1: bare list of highlight intervals
    if isinstance(data, list):
        return _upgrade_v1_list_to_v2(data)

    # v2: already normalized timeline object
    if isinstance(data, dict) and data.get("schema_version") == SCHEMA_VERSION:
        return data

    # Legacy object with embedded timeline but missing schema fields
    if isinstance(data, dict) and "timeline" in data:
        upgraded = _upgrade_v1_list_to_v2(data.get("timeline", []))
        return upgraded

    raise ValueError("Unsupported timeline format")


def save_timeline(path: Path, timeline_obj: Dict[str, Any]) -> None:
    """
    Persist a timeline object to disk in JSON format.

    This function does not validate schema correctness; it assumes
    the caller has already normalized the timeline structure.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(timeline_obj, f, indent=2)
