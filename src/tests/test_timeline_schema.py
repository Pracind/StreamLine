from pathlib import Path
from highlights.timeline_io import load_timeline, save_timeline

def test_v1_upgrade(tmp_path: Path):
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
    obj = {"schema_version": 2, "timeline": []}
    p = tmp_path / "timeline.json"
    save_timeline(p, obj)
    out = load_timeline(p)
    assert out["schema_version"] == 2
    assert out["timeline"] == []
