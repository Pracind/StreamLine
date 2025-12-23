from pathlib import Path
import sys

# ─────────────────────────────────────────────
# Environment detection
# ─────────────────────────────────────────────

IS_FROZEN = getattr(sys, "frozen", False)


# ─────────────────────────────────────────────
# Base directories
# ─────────────────────────────────────────────

if IS_FROZEN:
    # PyInstaller runtime
    BASE_DIR = Path(sys.executable).parent          # dist/VOD-Engine/
    INTERNAL_DIR = Path(sys._MEIPASS)                # dist/VOD-Engine/_internal/
else:
    # Development environment
    BASE_DIR = Path(__file__).resolve().parents[2]   # project root
    INTERNAL_DIR = BASE_DIR


# ─────────────────────────────────────────────
# Static bundled assets (READ-ONLY)
# ─────────────────────────────────────────────

ASSETS_DIR = INTERNAL_DIR / "assets"
KEYWORDS_PATH = ASSETS_DIR / "keywords.json"


# ─────────────────────────────────────────────
# Runtime-generated data (READ / WRITE)
# ─────────────────────────────────────────────

DATA_DIR = BASE_DIR / "data"

INPUT_DIR = DATA_DIR / "input"
CHUNKS_DIR = DATA_DIR / "chunks"
AUDIO_DIR = DATA_DIR / "audio"
TRANSCRIPTS_DIR = DATA_DIR / "transcripts"
HIGHLIGHTS_DIR = DATA_DIR / "highlights"
OUTPUT_DIR = DATA_DIR / "output"

# Create runtime directories only
for directory in (
    DATA_DIR,
    INPUT_DIR,
    CHUNKS_DIR,
    AUDIO_DIR,
    TRANSCRIPTS_DIR,
    HIGHLIGHTS_DIR,
    OUTPUT_DIR,
):
    directory.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────
# Processing configuration
# ─────────────────────────────────────────────

# Chunking
CHUNK_DURATION_SECONDS = 45
AUDIO_SAMPLE_RATE = 16000

# Audio analysis
SPIKE_THRESHOLD = 1.5
SILENCE_RMS_THRESHOLD = 1e-4

# Whisper
WHISPER_MODEL_NAME = "base"

# Scoring weights
AUDIO_WEIGHT = 0.7
TEXT_WEIGHT = 0.3

# Highlight selection
HIGHLIGHT_THRESHOLD = 0.65

# Highlight refinement
MERGE_GAP_SECONDS = 5
PRE_BUFFER_SECONDS = 5
POST_BUFFER_SECONDS = 5

# Highlight filtering
MIN_HIGHLIGHT_DURATION_SECONDS = 10


#Twitch Settings 
TWITCH_DIR = DATA_DIR / "twitch"
TWITCH_VOD_DIR = TWITCH_DIR / "vods"
TWITCH_META_DIR = TWITCH_DIR / "metadata"

for directory in (
    TWITCH_DIR,
    TWITCH_VOD_DIR,
    TWITCH_META_DIR,
):
    directory.mkdir(parents=True, exist_ok=True)


#Twitch Chat Settings
TWITCH_CHAT_DIR = TWITCH_DIR / "chat"
TWITCH_CHAT_RAW_DIR = TWITCH_CHAT_DIR / "raw"
TWITCH_DOWNLOADER_PATH = Path(
    r"C:\tools\TwitchDownloader\TwitchDownloaderCLI.exe"
)

for directory in (
    TWITCH_CHAT_DIR,
    TWITCH_CHAT_RAW_DIR,
):
    directory.mkdir(parents=True, exist_ok=True)