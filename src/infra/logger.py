"""
Logging setup utilities for Streamline.

This module configures a consistent logger that writes detailed logs to disk
and optionally mirrors informational output to stdout for CLI usage.
"""

import logging
from pathlib import Path
from datetime import datetime
import sys


def _get_log_dir() -> Path:
    """
    Resolve and create the directory used for log files.

    Behavior differs by execution environment:
    - Frozen executable: logs are written next to the binary
    - Source execution: logs are written under the project root
    """
    if getattr(sys, "frozen", False):
        # Executable mode: logs alongside the bundled binary
        base_dir = Path(sys.executable).parent
    else:
        # Development mode: logs under the project root
        base_dir = Path(__file__).resolve().parents[2]

    log_dir = base_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def setup_logger(ui_mode: bool = False):
    """
    Initialize and return the application logger.

    The logger:
    - Always writes DEBUG-level logs to a timestamped file
    - Optionally writes INFO-level logs to stdout when not in UI mode
    - Clears existing handlers to avoid duplicate output
    """
    log_dir = _get_log_dir()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = log_dir / f"run_{timestamp}.log"

    logger = logging.getLogger("vod-engine")
    logger.setLevel(logging.DEBUG)

    # Remove any pre-existing handlers to prevent duplicate logging
    logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    # File handler (always enabled, full verbosity)
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler (best-effort, CLI usage)
    if not ui_mode:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    logger.info("=== LOGGER INITIALIZED ===")
    logger.info("Log file: %s", log_path)

    return logger
