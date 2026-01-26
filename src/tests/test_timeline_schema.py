"""
Tests for timeline schema loading and upgrading.

This module validates backward compatibility and persistence behavior
for highlight timeline schema versions.
"""

from pathlib import Path
from highlights.timeline_io import load_timeline, save_timeline


def test_v1_upgrade(tmp_path: Path):
    """
    Verify that a legacy v1 timeline (bare list) is upgraded to schema v2.

    The test ensures:
    - schema_version is set correctly
    - timeline entries are preserved
    - required v2 default fields are populated
    """
    v1 = [
        {"start_time": 10, "end_time": 20, "chunk_ids": ["c1"]},
        {"start_time": 30, "end_time": 40, "chunk_ids": ["c2"]},
    ]
    p = tmp_path / "timeline.json"
    p.write_text(__import__("json").dumps(v1))

    data = load_timeline(p)
    assert data["schema_version"] == 2
    assert len(data["timeline"]) == 2
    assert data["timeline"][0]["enabled"] is True
    assert data["timeline"][0]["trim_start_offset"] == 0.0
    assert data["timeline"][0]["order_index"] == 0


def test_save_and_load_v2(tmp_path: Path):
    """
    Verify round-trip save and load behavior for a valid v2 timeline.

    Ensures that saving a schema v2 object and reloading it
    preserves structure and contents.
    """
    obj = {"schema_version": 2, "timeline": []}
    p = tmp_path / "timeline.json"
    save_timeline(p, obj)
    out = load_timeline(p)
    assert out["schema_version"] == 2
    assert out["timeline"] == []
