import shutil
from pathlib import Path

from src.config import DATA_DIR


DERIVED_DIRS = [
    DATA_DIR / "chunks",
    DATA_DIR / "audio",
    DATA_DIR / "highlights",
    DATA_DIR / "output",
    DATA_DIR / "logs",
]


def reset_derived_state():
    for path in DERIVED_DIRS:
        if path.exists():
            shutil.rmtree(path)
