from pathlib import Path
import sys

from src.config import INPUT_DIR
from src.config import CHUNKS_DIR

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



def get_input_video() -> Path:
    if not INPUT_DIR.exists():
        print(f"Input directory does not exist: {INPUT_DIR}")
        sys.exit(1)

    video_files = list(INPUT_DIR.glob("*.mp4"))

    if not video_files:
        print("No input video found in data/input/")
        print("Please place an .mp4 file in the input directory.")
        sys.exit(1)

    if CHUNKS_DIR.exists() and any(CHUNKS_DIR.iterdir()):
        print("Warning: Existing chunks will be overwritten.")

    # Phase 1 assumption: single input video
    return video_files[0]


if __name__ == "__main__":
    input_video = get_input_video()
    print(f"Using input video: {input_video}")

    chunks = chunk_video(str(input_video))
    print(f"Created {len(chunks)} chunks.")

    audio_count = extract_audio_from_chunks()
    print(f"Extracted audio from {audio_count} chunks.")

    rms_results = calculate_rms_energy()
    write_rms_to_metadata(rms_results)
    print("RMS energy calculated for all chunks.")

    transcripts = transcribe_audio_chunks()
    print(f"Transcribed {len(transcripts)} chunks.")

    text_features = count_keyword_hits_per_chunk()
    print(f"Keyword hits counted for {len(text_features)} chunks.")

    merge_text_scores_into_chunks()
    print("Text scores merged into chunk metadata.")

    apply_final_scores_to_chunks()
    print("Final scores computed for all chunks.")

    highlight_count = flag_highlight_chunks()
    print(f"Flagged {highlight_count} highlight chunks.")

    logged = log_scores_for_tuning()
    print(f"Logged scores for {logged} chunks.")

    merged = merge_adjacent_highlights()
    print(f"Merged into {len(merged)} highlight segments.")

    buffered = add_buffers_to_highlights()
    print(f"Buffered {len(buffered)} highlight segments.")

    final_timeline = filter_short_highlights()
    print(f"Final highlight timeline has {len(final_timeline)} clips.")


    
