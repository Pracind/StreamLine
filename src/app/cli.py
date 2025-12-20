from pathlib import Path
import sys
import argparse
import traceback
import os
import psutil

from src.infra.config import INPUT_DIR, CHUNKS_DIR

from src.processing.video_chunker import chunk_video
from src.processing.audio_extractor import extract_audio_from_chunks
from src.processing.audio_rms import calculate_rms_energy, write_rms_to_metadata
from src.processing.transcriber import transcribe_audio_chunks
from src.scoring.text_features import count_keyword_hits_per_chunk
from src.scoring.score_merger import merge_text_scores_into_chunks
from src.scoring.scoring import apply_final_scores_to_chunks
from src.highlights.highlight_selector import flag_highlight_chunks
from src.scoring.score_logger import log_scores_for_tuning
from src.highlights.highlight_merger import merge_adjacent_highlights
from src.highlights.highlight_buffer import add_buffers_to_highlights
from src.highlights.highlight_filter import filter_short_highlights
from src.highlights.clip_extractor import extract_highlight_clips
from src.highlights.clip_concatenator import concatenate_clips
from src.output.final_encoder import encode_final_video
from src.pipeline.reset import reset_derived_state
from src.infra.logger import setup_logger
from src.output.cleanup import cleanup_temporary_files



TOTAL_STEPS = 14


def parse_args():
    parser = argparse.ArgumentParser(
        description="VOD-Engine — Generate highlights from a VOD"
    )
    parser.add_argument(
        "--input",
        type=Path,
        help="Path to input .mp4 video (optional)"
    )
    
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from existing intermediate results"
    )
    return parser.parse_args()


def log_memory(logger, label: str):
    process = psutil.Process(os.getpid())
    mem_mb = process.memory_info().rss / (1024 * 1024)
    logger.info(f"Memory usage [{label}]: {mem_mb:.1f} MB")


def get_input_video(cli_input: Path | None) -> Path:
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
    progress_callback=None,
):
    print(">>> RUN_PIPELINE ENTERED <<<", flush=True)
    step = 1

    def report(message: str):
        if progress_callback:
            progress_callback(step, TOTAL_STEPS, message)

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
    transcribe_audio_chunks(logger)
    step += 1

    report("Scoring text features")
    count_keyword_hits_per_chunk()
    step += 1

    report("Merging text scores")
    merge_text_scores_into_chunks()
    step += 1

    report("Computing final highlight scores")
    apply_final_scores_to_chunks()
    step += 1

    report("Selecting highlight chunks")
    flag_highlight_chunks()
    step += 1

    report("Logging scores for tuning")
    log_scores_for_tuning()
    step += 1

    report("Merging adjacent highlights")
    merge_adjacent_highlights()
    step += 1

    report("Adding buffers to highlights")
    add_buffers_to_highlights()
    step += 1

    report("Filtering short highlights")
    filter_short_highlights()
    step += 1

    report("Extracting highlight clips")
    extract_highlight_clips(input_video, logger, resume)
    step += 1

    report("Concatenating and encoding final video")
    concatenate_clips()
    encode_final_video()
    cleanup_temporary_files(logger)


    




def main():
    args = parse_args()
    reset_derived_state(args.resume)
    logger = setup_logger()

    input_video = get_input_video(args.input)

    try:
        run_pipeline(input_video, args.resume, logger)
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception:
        sys.exit(1)
    



if __name__ == "__main__":
    main()
