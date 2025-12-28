# src/debug/timeline_cli.py

import json
from infra.config import CHUNKS_DIR, OUTPUT_DIR

TIMELINE_TXT = OUTPUT_DIR / "timeline.txt"
TIMELINE_JSON = OUTPUT_DIR / "timeline.json"


def render_timeline(print_cli: bool = True, save: bool = True):
    """
    Timeline rendering strategy:
    1. If timeline.txt exists → load & display
    2. Else if chunks.json exists → generate timeline and save
    3. Else → error
    """

    # ─── CASE 1: Load existing timeline ─────────────────────────────
    if TIMELINE_TXT.exists():
        timeline_text = TIMELINE_TXT.read_text(encoding="utf-8")

        if print_cli:
            print(timeline_text)

        return timeline_text

    # ─── CASE 2: Generate from chunks.json ──────────────────────────
    chunks_path = CHUNKS_DIR / "chunks.json"
    if not chunks_path.exists():
        raise RuntimeError(
            "No timeline available. Run the pipeline at least once."
        )

    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    lines = []
    timeline_json = []

    header = "\n=== HIGHLIGHT TIMELINE ===\n"
    lines.append(header)

    for entry in chunks:
        start = int(entry["start_time"])
        end = int(entry["end_time"])

        a = entry.get("audio_score", 0.0)
        t = entry.get("text_score", 0.0)
        c = entry.get("chat_boost", 0.0)
        f = entry.get("final_score", 0.0)

        is_highlight = entry.get("is_highlight", False)
        reason = entry.get("highlight_reason", "")

        time_str = f"[{_fmt(start)}–{_fmt(end)}]"
        score_str = f"A:{a:.2f}  T:{t:.2f}  C:+{c:.2f}  F:{f:.2f}"

        marker = "★" if is_highlight else "┆"
        reason_str = f" {reason}" if reason else ""

        line = f"{time_str}  {score_str}  {marker}{reason_str}"
        lines.append(line)

        timeline_json.append({
            "start_sec": start,
            "end_sec": end,
            "audio": a,
            "text": t,
            "chat": c,
            "final": f,
            "highlight": is_highlight,
            "reason": reason or None,
        })

    footer = "\nLegend: ★ = highlight\n"
    lines.append(footer)

    timeline_text = "\n".join(lines)

    if print_cli:
        print(timeline_text)

    if save:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        TIMELINE_TXT.write_text(timeline_text, encoding="utf-8")
        TIMELINE_JSON.write_text(
            json.dumps(timeline_json, indent=2),
            encoding="utf-8",
        )

    return timeline_text


def _fmt(seconds: int) -> str:
    m = seconds // 60
    s = seconds % 60
    return f"{m:02d}:{s:02d}"
