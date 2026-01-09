import json
from pathlib import Path
from typing import Dict, Any, List

SCHEMA_VERSION = 2


def _upgrade_v1_list_to_v2(raw_list: List[Dict[str, Any]]) -> Dict[str, Any]:
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
    if not path.exists():
        return {"schema_version": SCHEMA_VERSION, "timeline": []}

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # v1: bare list
    if isinstance(data, list):
        return _upgrade_v1_list_to_v2(data)

    # v2: wrapped object
    if isinstance(data, dict) and data.get("schema_version") == SCHEMA_VERSION:
        return data

    # Unknown/older: best-effort upgrade
    if isinstance(data, dict) and "timeline" in data:
        # assume items but missing fields
        upgraded = _upgrade_v1_list_to_v2(data.get("timeline", []))
        return upgraded

    raise ValueError("Unsupported timeline format")


def save_timeline(path: Path, timeline_obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(timeline_obj, f, indent=2)
