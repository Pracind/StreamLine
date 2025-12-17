from pathlib import Path

# Directories
DATA_DIR = Path("data")
INPUT_DIR = DATA_DIR / "input"
CHUNKS_DIR = DATA_DIR / "chunks"
AUDIO_DIR = DATA_DIR / "audio"

# Chunking
CHUNK_DURATION_SECONDS = 45
AUDIO_SAMPLE_RATE = 16000