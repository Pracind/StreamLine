"""
Reset derived pipeline state.

This module removes all directories containing artifacts derived from
previous runs, allowing the pipeline to start from a clean state.
"""

import shutil
from pathlib import Path

from infra.config import DATA_DIR


# Directories that contain derived or regenerable pipeline artifacts
DERIVED_DIRS = [
    DATA_DIR / "chunks",
    DATA_DIR / "audio",
    DATA_DIR / "highlights",
    DATA_DIR / "output",
]


def reset_derived_state(resume: bool):
    """
    Reset derived pipeline state unless resuming.

    If resume is True, this function is a no-op.
    Otherwise, all derived directories are removed recursively.
    """
    if resume:
        return

    for path in DERIVED_DIRS:
        if path.exists():
            shutil.rmtree(path)
