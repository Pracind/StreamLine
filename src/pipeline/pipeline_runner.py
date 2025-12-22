from pathlib import Path
import shutil

from app.cli import run_pipeline
from infra.config import INPUT_DIR, CHUNKS_DIR
from pipeline.reset import reset_derived_state
from infra.logger import setup_logger


def run_pipeline_from_ui(input_video: Path, progress_callback=None):
    logger = setup_logger()

    input_video = Path(input_video).resolve()
    if not input_video.exists():
        raise FileNotFoundError(input_video)

    # 🔴 HARD RESET — UI always starts fresh
    reset_derived_state(resume=False)

    INPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Remove previous inputs
    for f in INPUT_DIR.glob("*.mp4"):
        f.unlink()

    staged_input = INPUT_DIR / input_video.name
    shutil.copy2(input_video, staged_input)

    run_pipeline(
        input_video=staged_input,
        resume=False,
        logger=logger,
        progress_callback=progress_callback,
    )
