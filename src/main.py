from pathlib import Path
import sys
import argparse
import traceback

from src.config import INPUT_DIR, CHUNKS_DIR

from src.video_chunker import chunk_video
from src.audio_extractor import extract_audio_from_chunks
from src.audio_rms import calculate_rms_energy, write_rms_to_metadata
from src.transcriber import transcribe_audio_chunks
from src.text_features import count_keyword_hits_per_chunk
from src.score_merger import merge_text_scores_into_chunks
from src.scoring import apply_final_scores_to_chunks
from src.highlight_selector import flag_highlight_chunks
from src.score_logger import log_scores_for_tuning
from src.highlight_merger import merge_adjacent_highlights
from src.highlight_buffer import add_buffers_to_highlights
from src.highlight_filter import filter_short_highlights
from src.clip_extractor import extract_highlight_clips
from src.clip_concatenator import concatenate_clips
from src.final_encoder import encode_final_video
from src.run_reset import reset_derived_state


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
    return parser.parse_args()


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


def progress(step: int, total: int, message: str):
    print(f"[{step}/{total}] {message}")


def main():
    print("VOD-Engine — Generating highlights")
    reset_derived_state()

    args = parse_args()
    input_video = get_input_video(args.input)

    step = 1

    try:
        progress(step, TOTAL_STEPS, "Chunking input video")
        chunks = chunk_video(str(input_video))
        print(f"  → {len(chunks)} chunks created")
        step += 1

        progress(step, TOTAL_STEPS, "Extracting audio from chunks")
        audio_count = extract_audio_from_chunks()
        print(f"  → {audio_count} audio files extracted")
        step += 1

        progress(step, TOTAL_STEPS, "Calculating audio RMS energy")
        rms_results = calculate_rms_energy()
        write_rms_to_metadata(rms_results)
        step += 1

        progress(step, TOTAL_STEPS, "Transcribing audio (Whisper)")
        transcripts = transcribe_audio_chunks()
        print(f"  → {len(transcripts)} transcripts generated")
        step += 1

        progress(step, TOTAL_STEPS, "Scoring text features")
        count_keyword_hits_per_chunk()
        step += 1

        progress(step, TOTAL_STEPS, "Merging text scores")
        merge_text_scores_into_chunks()
        step += 1

        progress(step, TOTAL_STEPS, "Computing final highlight scores")
        apply_final_scores_to_chunks()
        step += 1

        progress(step, TOTAL_STEPS, "Selecting highlight chunks")
        highlight_count = flag_highlight_chunks()
        print(f"  → {highlight_count} highlight chunks flagged")
        step += 1

        progress(step, TOTAL_STEPS, "Logging scores for tuning")
        log_scores_for_tuning()
        step += 1

        progress(step, TOTAL_STEPS, "Merging adjacent highlights")
        merged = merge_adjacent_highlights()
        print(f"  → {len(merged)} merged highlight segments")
        step += 1

        progress(step, TOTAL_STEPS, "Adding buffers to highlights")
        buffered = add_buffers_to_highlights()
        print(f"  → {len(buffered)} buffered segments")
        step += 1

        progress(step, TOTAL_STEPS, "Filtering short highlights")
        final_timeline = filter_short_highlights()
        print(f"  → {len(final_timeline)} final highlight clips")
        step += 1

        progress(step, TOTAL_STEPS, "Extracting highlight clips")
        clips = extract_highlight_clips(input_video)
        print(f"  → {len(clips)} clips extracted")
        step += 1

        progress(step, TOTAL_STEPS, "Concatenating and encoding final video")
        concatenate_clips()
        final_encoded = encode_final_video()
        step += 1

    except Exception as e:
        print("\n❌ ERROR: Highlight generation failed.")
        print(f"Reason: {e}")
        print("\n--- Debug Traceback (for developer) ---")
        traceback.print_exc()
        sys.exit(1)

    print("\n✅ Highlight generation complete")
    print(f"Final video: {final_encoded}")


if __name__ == "__main__":
    main()
