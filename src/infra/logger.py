import logging
from pathlib import Path
from datetime import datetime
import sys


def _get_log_dir() -> Path:
    if getattr(sys, "frozen", False):
        # EXE mode: logs next to the executable
        base_dir = Path(sys.executable).parent
    else:
        # Dev mode: project root
        base_dir = Path(__file__).resolve().parents[2]

    log_dir = base_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def setup_logger(ui_mode: bool = False):
    log_dir = _get_log_dir()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = log_dir / f"run_{timestamp}.log"

    logger = logging.getLogger("vod-engine")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    # File handler (ALWAYS)
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler (best-effort)
    if not ui_mode:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    logger.info("=== LOGGER INITIALIZED ===")
    logger.info("Log file: %s", log_path)

    return logger
