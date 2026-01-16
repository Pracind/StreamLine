"""
CLI utility for rendering a human-readable highlight timeline.

This module is intentionally read-only with respect to pipeline state:
it either displays a previously generated timeline or derives one
from persisted chunk metadata for debugging and inspection purposes.
"""

import json
from infra.config import CHUNKS_DIR, OUTPUT_DIR

# Output locations for rendered timelines
TIMELINE_TXT = OUTPUT_DIR / "timeline.txt"
TIMELINE_JSON = OUTPUT_DIR / "timeline.json"


def render_timeline(print_cli: bool = True, save: bool = True):
    """
    Render a textual and JSON timeline of chunk-level scores and highlights.

    Resolution strategy:
    1. If a saved timeline.txt exists, load and optionally print it.
    2. Otherwise, derive a timeline from chunks.json and optionally persist it.
    3. If neither source exists, raise an error indicating no prior run.
    """

    # ─── Case 1: Load an existing rendered timeline ────────────────────────────
    if TIMELINE_TXT.exists():
        timeline_text = TIMELINE_TXT.read_text(encoding="utf-8")

        if print_cli:
            print(timeline_text)

        return timeline_text




    # ─── Case 2: Generate timeline from chunk metadata ──────────────────────────
    chunks_path = CHUNKS_DIR / "chunks.json"
    if not chunks_path.exists():
        raise RuntimeError(
            "No timeline available. Run the pipeline at least once."
        )

    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    lines = []
    timeline_json = []




    # Human-readable header
    header = "\n=== HIGHLIGHT TIMELINE ===\n"
    lines.append(header)

    for entry in chunks:
        # Time boundaries (seconds)
        start = int(entry["start_time"])
        end = int(entry["end_time"])

        # Individual score components
        a = entry.get("audio_score", 0.0)
        t = entry.get("text_score", 0.0)
        c = entry.get("chat_boost", 0.0)
        f = entry.get("final_score", 0.0)

        # Highlight classification metadata
        is_highlight = entry.get("is_highlight", False)
        reason = entry.get("highlight_reason", "")

        # CLI formatting
        time_str = f"[{_fmt(start)}–{_fmt(end)}]"
        score_str = f"A:{a:.2f}  T:{t:.2f}  C:+{c:.2f}  F:{f:.2f}"

        marker = "★" if is_highlight else "┆"
        reason_str = f" {reason}" if reason else ""

        line = f"{time_str}  {score_str}  {marker}{reason_str}"
        lines.append(line)

        # Structured representation for JSON output
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




    # Footer legend for CLI interpretation
    footer = "\nLegend: ★ = highlight\n"
    lines.append(footer)

    timeline_text = "\n".join(lines)

    if print_cli:
        print(timeline_text)




    # Persist rendered outputs if requested
    if save:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        TIMELINE_TXT.write_text(timeline_text, encoding="utf-8")
        TIMELINE_JSON.write_text(
            json.dumps(timeline_json, indent=2),
            encoding="utf-8",
        )

    return timeline_text


def _fmt(seconds: int) -> str:
    """
    Format a second offset as MM:SS for timeline display.
    """
    m = seconds // 60
    s = seconds % 60
    return f"{m:02d}:{s:02d}"
