"""
CLI entry point for Streamline.

This module wires together the entire VOD → scoring → highlights → encoding
pipeline and exposes it via command-line flags. It is intentionally procedural
and orchestration-focused: all domain logic lives in downstream modules.
"""

from pathlib import Path
import sys
import argparse
import traceback
import os
import psutil

from infra.config import INPUT_DIR, CHUNKS_DIR
from infra import config

# ─── Core Processing Pipeline Imports ──────────────────────────────────────────
from processing.video_chunker import chunk_video
from processing.audio_extractor import extract_audio_from_chunks
from processing.audio_rms import calculate_rms_energy, write_rms_to_metadata
from processing.transcriber import transcribe_audio_chunks

# ─── Scoring Imports ───────────────────────────────────────────────────────────
from scoring.text_features import count_keyword_hits_per_chunk
from scoring.score_merger import merge_text_scores_into_chunks
from scoring.scoring import apply_final_scores_to_chunks
from scoring.score_logger import log_scores_for_tuning
from scoring.chat_boost import apply_chat_boost_to_chunks
from scoring.presets import load_preset, save_preset

# ─── Highlight Generation Imports ──────────────────────────────────────────────
from highlights.highlight_selector import flag_highlight_chunks
from highlights.highlight_merger import merge_adjacent_highlights
from highlights.highlight_buffer import add_buffers_to_highlights
from highlights.highlight_filter import filter_short_highlights
from highlights.false_positive_filter import filter_false_positive_highlights
from highlights.clip_extractor import extract_highlight_clips
from highlights.clip_concatenator import concatenate_clips

# ─── Output & Cleanup Imports ──────────────────────────────────────────────────
from output.final_encoder import encode_final_video
from output.cleanup import cleanup_temporary_files

# ─── Pipeline Control & Debugging ──────────────────────────────────────────────
from pipeline.reset import reset_derived_state
from infra.logger import setup_logger
from debug.timeline_cli import render_timeline

# ─── Chat Processing Imports (Phase 2) ─────────────────────────────────────────
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


# Total number of logical pipeline steps, used for progress reporting
TOTAL_STEPS = 14


def parse_args():
    """
    Parse and validate CLI arguments.

    This function defines all user-facing execution modes, including:
    - Local file vs Twitch VOD input
    - Resume / rebuild behavior
    - Timeline-only debug rendering
    - Chat influence configuration
    - Scoring preset load/save
    """
    parser = argparse.ArgumentParser(
        description="VOD-Engine — Generate highlights from a VOD"
    )

    # Input source is mutually exclusive: local file OR Twitch VOD
    input_group = parser.add_mutually_exclusive_group()

    input_group.add_argument(
        "--input",
        type=Path,
        help="Path to input .mp4 video"
    )

    input_group.add_argument(
        "--twitch-vod",
        type=str,
        help="Twitch VOD URL"
    )

    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from existing intermediate results"
    )

    parser.add_argument(
        "--timeline",
        action="store_true",
        help="Print debug timeline of chunk scores"
    )

    parser.add_argument(
        "--chat-weight",
        type=float,
        default=None,
        help="Scale chat influence (0.0 = off, 1.0 = default)",
    )

    parser.add_argument(
        "--no-chat",
        action="store_true",
        help="Disable chat-based scoring (Phase 2)"
    )

    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Rebuild final video from edited timeline without re-running analysis",
    )

    parser.add_argument("--preset", type=str, help="Load scoring preset")
    parser.add_argument("--save-preset", type=str, help="Save current scoring as preset")

    return parser.parse_args()


def log_memory(logger, label: str):
    """
    Log current process RSS memory usage for debugging and profiling.
    """
    process = psutil.Process(os.getpid())
    mem_mb = process.memory_info().rss / (1024 * 1024)
    logger.info(f"Memory usage [{label}]: {mem_mb:.1f} MB")


def get_input_video(cli_input: Path | None) -> Path:
    """
    Resolve and validate the input video path.

    Priority:
    1. Explicit --input path (must exist and be .mp4)
    2. First .mp4 found in INPUT_DIR

    Exits the process with a user-facing error message on failure.
    """
    if cli_input:
        if not cli_input.exists():
            print(f"ERROR: Input file does not exist: {cli_input}")
            sys.exit(1)

        if cli_input.suffix.lower() != ".mp4":
            print("ERROR: Input file must be an .mp4")
            sys.exit(1)

        return cli_input

    if not INPUT_DIR.exists():
        print(f"ERROR: Input directory does not exist: {INPUT_DIR}")
        sys.exit(1)

    video_files = list(INPUT_DIR.glob("*.mp4"))

    if not video_files:
        print("ERROR: No input video found in data/input/")
        print("Please place an .mp4 file in the input directory.")
        sys.exit(1)

    if CHUNKS_DIR.exists() and any(CHUNKS_DIR.iterdir()):
        print("Warning: Existing chunks will be overwritten.")

    return video_files[0]


def run_pipeline(
    input_video: Path,
    resume: bool,
    logger,
    chat_weight: float = 1.0,
    progress_callback=None,
):
    """
    Execute the full end-to-end Streamline pipeline.

    This function is intentionally linear and imperative to make
    execution order, side effects, and progress reporting explicit.
    """
    print(">>> RUN_PIPELINE ENTERED <<<", flush=True)
    step = 1

    def report(message: str):
        """
        Emit progress updates to an optional UI callback.
        """
        if progress_callback:
            progress_callback(step, TOTAL_STEPS, message)




    # ─── Phase 1: Signal Extraction ────────────────────────────────────────────
    report("Chunking input video")
    chunks = chunk_video(str(input_video), logger)
    step += 1

    report("Extracting audio from chunks")
    extract_audio_from_chunks(logger, resume)
    step += 1

    report("Calculating audio RMS energy")
    rms_results = calculate_rms_energy(logger, resume)
    write_rms_to_metadata(rms_results)
    step += 1

    report("Transcribing audio (Whisper)")
    transcribe_audio_chunks(logger, resume)
    step += 1

    logger.info(">>> AFTER TRANSCRIPTION — ENTERING SCORING <<<")




    # ─── Phase 2: Scoring ──────────────────────────────────────────────────────
    report("Scoring text features")
    count_keyword_hits_per_chunk(logger)
    logger.info("STEP %d DONE: text features", step)
    step += 1

    report("Merging text scores")
    merge_text_scores_into_chunks()
    logger.info("STEP %d DONE: merge scoring", step)
    step += 1

    report("Computing final highlight scores")
    apply_final_scores_to_chunks()
    apply_chat_boost_to_chunks(logger, chat_weight)
    logger.info("STEP %d DONE: final scoring", step)
    step += 1




    # ─── Phase 3: Highlight Selection & Refinement ─────────────────────────────
    report("Selecting highlight chunks")
    flag_highlight_chunks()
    logger.info("STEP %d DONE: selecting highlights", step)
    step += 1

    report("Logging scores for tuning")
    log_scores_for_tuning()
    logger.info("STEP %d DONE: logging scoring", step)
    step += 1

    report("Merging adjacent highlights")
    merge_adjacent_highlights()
    logger.info("STEP %d DONE: merging highlights", step)
    step += 1

    report("Adding buffers to highlights")
    add_buffers_to_highlights()
    logger.info("STEP %d DONE: adding buffer", step)
    step += 1

    report("Filtering short highlights")
    filter_short_highlights()
    filter_false_positive_highlights()
    logger.info("STEP %d DONE: filtering highlights", step)
    step += 1




    # ─── Phase 4: Clip Extraction & Encoding ───────────────────────────────────
    report("Extracting highlight clips")
    extract_highlight_clips(input_video, logger, resume)
    step += 1

    report("Concatenating and encoding final video")
    concatenate_clips()
    encode_final_video()
    render_timeline()
    cleanup_temporary_files(logger)


def rebuild_from_timeline(input_video: Path, logger, resume=True):
    """
    Rebuild the final output video from an existing, possibly edited timeline.

    This skips all analysis and scoring stages and only re-executes
    clip extraction and encoding.
    """
    logger.info(">>> REBUILDING FROM TIMELINE <<<")

    extract_highlight_clips(input_video, logger, resume)
    concatenate_clips()
    encode_final_video()

    logger.info(">>> REBUILD COMPLETE <<<")


def main():
    """
    Primary CLI entry point.

    Responsible for:
    - Argument parsing
    - Environment setup
    - Mode dispatch (timeline-only, rebuild, full pipeline)
    """
    args = parse_args()
    logger = setup_logger()

    if args.preset:
        load_preset(args.preset)
        logger.info("Loaded preset: %s", args.preset)

    if args.save_preset:
        save_preset(args.save_preset)
        logger.info("Saved preset: %s", args.save_preset)




    # ─── Timeline-Only Debug Mode ──────────────────────────────────────────────
    if args.timeline and not args.twitch_vod and not args.input:
        render_timeline(print_cli=True, save=False)
        return

    reset_derived_state(args.resume)

    if args.no_chat:
        config.ENABLE_CHAT_INFLUENCE = False
        logger.info("Chat influence DISABLED via CLI flag")

    if not (args.input or args.twitch_vod):
        print("ERROR: one of --input or --twitch-vod is required")
        sys.exit(2)

    if args.chat_weight is not None:
        config.CHAT_WEIGHT = max(0.0, args.chat_weight)
        logger.info("Chat weight set to %.2f via CLI", config.CHAT_WEIGHT)




    # ─── Twitch VOD Flow (includes chat processing) ────────────────────────────
    if args.twitch_vod:
        from infra.twitch import resolve_twitch_vod
        vod_meta = resolve_twitch_vod(args.twitch_vod, logger)
        input_video = vod_meta.local_video_path

        if args.timeline:
            render_timeline(print_cli=True, save=False)
            return

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




    # ─── Rebuild Mode ──────────────────────────────────────────────────────────
    if args.rebuild:
        if args.input:
            input_video = get_input_video(args.input)
        elif args.twitch_vod:
            from infra.twitch import resolve_twitch_vod
            vod_meta = resolve_twitch_vod(args.twitch_vod, logger)
            input_video = vod_meta.local_video_path
        else:
            print("ERROR: --rebuild requires --input or --twitch-vod")
            sys.exit(2)

        rebuild_from_timeline(input_video, logger, resume=True)
        return




    # ─── Full Pipeline Execution ───────────────────────────────────────────────
    input_video = get_input_video(args.input)

    try:
        run_pipeline(input_video, args.resume, logger)
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception:
        sys.exit(1)


if __name__ == "__main__":
    main()
