from pathlib import Path
import shutil

from app.cli import run_pipeline
from infra.config import INPUT_DIR, CHUNKS_DIR
from pipeline.reset import reset_derived_state
from infra.logger import setup_logger
from infra.twitch import resolve_twitch_vod
from ui.input_modes import InputMode

def run_pipeline_from_ui(input_value, input_mode, progress_callback=None):
    logger = setup_logger()

    reset_derived_state(resume=False)

    if input_mode == InputMode.LOCAL:
        input_video = Path(input_value).resolve()
        if not input_video.exists():
            raise FileNotFoundError(input_video)

        INPUT_DIR.mkdir(parents=True, exist_ok=True)
        for f in INPUT_DIR.glob("*.mp4"):
            f.unlink()

        staged_input = INPUT_DIR / input_video.name
        shutil.copy2(input_video, staged_input)
        input_video = staged_input

    elif input_mode == InputMode.TWITCH_URL:
        vod_meta = resolve_twitch_vod(input_value, logger)
        input_video = vod_meta.local_video_path

    elif input_mode == InputMode.TWITCH_ID:
        vod_url = f"https://www.twitch.tv/videos/{input_value}"
        vod_meta = resolve_twitch_vod(vod_url, logger)
        input_video = vod_meta.local_video_path

    else:
        raise ValueError(f"Unknown input mode: {input_mode}")

    run_pipeline(
        input_video=input_video,
        resume=False,
        logger=logger,
        progress_callback=progress_callback,
    )
