import shutil
from pathlib import Path

from src.infra.config import DATA_DIR


DERIVED_DIRS = [
    DATA_DIR / "chunks",
    DATA_DIR / "audio",
    DATA_DIR / "highlights",
    DATA_DIR / "output",
]


def reset_derived_state(resume: bool):
    if resume:
        return

    for path in DERIVED_DIRS:
        if path.exists():
            shutil.rmtree(path)
