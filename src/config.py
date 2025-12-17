from pathlib import Path

# Directories
DATA_DIR = Path("data")
INPUT_DIR = DATA_DIR / "input"
CHUNKS_DIR = DATA_DIR / "chunks"
AUDIO_DIR = DATA_DIR / "audio"

# Chunking
CHUNK_DURATION_SECONDS = 60
AUDIO_SAMPLE_RATE = 16000

# Audio spike detection
SPIKE_THRESHOLD = 1.5
SILENCE_RMS_THRESHOLD = 1e-4

# Whisper transcription
WHISPER_MODEL_NAME = "base"
TRANSCRIPTS_DIR = DATA_DIR / "transcripts"

# Scoring weights (Phase 1)
AUDIO_WEIGHT = 0.7
TEXT_WEIGHT = 0.3

# Highlight selection
HIGHLIGHT_THRESHOLD = 0.65

# Highlight refinement
MERGE_GAP_SECONDS = 5
PRE_BUFFER_SECONDS = 5
POST_BUFFER_SECONDS = 5