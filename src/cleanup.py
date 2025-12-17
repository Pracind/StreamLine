import shutil
from pathlib import Path

from src.config import DATA_DIR


def cleanup_temporary_files(logger):
    """
    Remove intermediate files that are not needed after a successful run.
    """
    logger.info("Starting temporary file cleanup")

    paths_to_remove = [
        DATA_DIR / "output" / "clips",
        DATA_DIR / "output" / "concat_list.txt",
        DATA_DIR / "output" / "highlights_raw.mp4",
    ]

    for path in paths_to_remove:
        if path.exists():
            try:
                if path.is_dir():
                    shutil.rmtree(path)
                    logger.info(f"Removed directory: {path}")
                else:
                    path.unlink()
                    logger.info(f"Removed file: {path}")
            except Exception as e:
                logger.warning(
                    f"Failed to clean up temporary path: {path} ({e})"
                )

    logger.info("Temporary file cleanup complete")
