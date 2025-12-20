from pathlib import Path
from src.app.cli import run_pipeline
from src.infra.logger import setup_logger


def run_pipeline_from_ui(input_video: Path, progress_callback=None):

    logger = setup_logger()

    print("here")

    run_pipeline(
        input_video=input_video,
        resume=False,
        logger=logger,
        progress_callback=progress_callback,
    )

    print("after here")
