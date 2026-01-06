from pathlib import Path
import shutil

import infra.config as config
from app.cli import run_pipeline
from infra.config import INPUT_DIR
from pipeline.reset import reset_derived_state
from infra.logger import setup_logger
from infra.twitch import resolve_twitch_vod
from ui.input_modes import InputMode


from processing.chat.activity_metrics import compute_messages_per_second
from processing.chat.baseline_metrics import compute_rolling_baseline
from processing.chat.spike_detection import detect_chat_spikes
from processing.chat.emote_metrics import compute_emote_density_per_second
from processing.chat.emote_repetition import detect_repeated_emotes
from processing.chat.emote_score import compute_emote_score
from processing.chat.keyword_metrics import compute_chat_keyword_hits
from processing.chat.keyword_score import compute_chat_keyword_score
from processing.chat.chat_score import compute_chat_score
from processing.chat.chat_smoothing import smooth_chat_score
from processing.chat.chat_export import export_final_chat_scores
from processing.chat.chat_alignment import align_chat_to_video


def run_pipeline_from_ui(
    input_value,
    input_mode: InputMode,
    chat_enabled: bool = True,
    chat_weight: float = 1.0,
    progress_callback=None,
):
    logger = setup_logger()

    # UI always starts fresh
    reset_derived_state(resume=False)

    # ─────────────────────────────────────────────
    # APPLY RUNTIME FLAGS
    # ─────────────────────────────────────────────
    config.ENABLE_CHAT_INFLUENCE = chat_enabled
    logger.info(
        "Chat influence %s via UI",
        "ENABLED" if chat_enabled else "DISABLED",
    )

    # ─────────────────────────────────────────────
    # Resolve input
    # ─────────────────────────────────────────────
    if input_mode == InputMode.LOCAL:
        input_video = Path(input_value).resolve()
        if not input_video.exists():
            raise FileNotFoundError(input_video)

        INPUT_DIR.mkdir(parents=True, exist_ok=True)

        # Clear previous inputs
        for f in INPUT_DIR.glob("*.mp4"):
            f.unlink()

        staged_input = INPUT_DIR / input_video.name
        shutil.copy2(input_video, staged_input)
        input_video = staged_input

    elif input_mode == InputMode.TWITCH_URL:
        vod_meta = resolve_twitch_vod(input_value, logger)
        input_video = vod_meta.local_video_path

        if chat_enabled:
            logger.info("Running chat metrics (UI mode)")
            compute_messages_per_second(logger)
            compute_rolling_baseline(logger)
            detect_chat_spikes(logger)
            compute_emote_density_per_second(logger)
            detect_repeated_emotes(logger)
            compute_emote_score(logger)
            compute_chat_keyword_hits(logger)
            compute_chat_keyword_score(logger)
            compute_chat_score(logger)
            smooth_chat_score(logger)
            export_final_chat_scores(logger)
            align_chat_to_video(logger, vod_meta.duration_seconds)

    elif input_mode == InputMode.TWITCH_ID:
        vod_url = f"https://www.twitch.tv/videos/{input_value}"
        vod_meta = resolve_twitch_vod(vod_url, logger)
        input_video = vod_meta.local_video_path

        if chat_enabled:
            logger.info("Running chat metrics (UI mode)")
            compute_messages_per_second(logger)
            compute_rolling_baseline(logger)
            detect_chat_spikes(logger)
            compute_emote_density_per_second(logger)
            detect_repeated_emotes(logger)
            compute_emote_score(logger)
            compute_chat_keyword_hits(logger)
            compute_chat_keyword_score(logger)
            compute_chat_score(logger)
            smooth_chat_score(logger)
            export_final_chat_scores(logger)
            align_chat_to_video(logger, vod_meta.duration_seconds)

    else:
        raise ValueError(f"Unknown input mode: {input_mode}")

    # ─────────────────────────────────────────────
    # Run pipeline
    # ─────────────────────────────────────────────
    run_pipeline(
        input_video=input_video,
        resume=False,
        logger=logger,
        progress_callback=progress_callback,
        chat_weight=chat_weight,
    )
