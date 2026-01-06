from pathlib import Path
import sys

# ─────────────────────────────────────────────
# Feature Toggles (GLOBAL)
# ─────────────────────────────────────────────

ENABLE_CHAT_INFLUENCE = True

CHAT_WEIGHT = 1.0 
CHAT_BOOST_MAX = 0.25

ENABLE_CHAT_ONLY_HIGHLIGHTS = False

# Threshold for chat-only highlights
CHAT_ONLY_THRESHOLD = 0.18
CHAT_ONLY_MIN_SCORE = 0.35


# ─────────────────────────────────────────────
# Environment Detection
# ─────────────────────────────────────────────

IS_FROZEN = getattr(sys, "frozen", False)


# ─────────────────────────────────────────────
# Base Directories
# ─────────────────────────────────────────────

if IS_FROZEN:
    BASE_DIR = Path(sys.executable).parent
    INTERNAL_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).resolve().parents[2]
    INTERNAL_DIR = BASE_DIR


# ─────────────────────────────────────────────
# Static Assets (READ-ONLY)
# ─────────────────────────────────────────────

ASSETS_DIR = INTERNAL_DIR / "assets"

KEYWORDS_PATH = ASSETS_DIR / "keywords.json"
CHAT_KEYWORDS_PATH = ASSETS_DIR / "chat_keywords.json"
HYPE_EMOTES_PATH = ASSETS_DIR / "hype_emotes.json"


# ─────────────────────────────────────────────
# Runtime Data Directories
# ─────────────────────────────────────────────

DATA_DIR = BASE_DIR / "data"

INPUT_DIR = DATA_DIR / "input"
CHUNKS_DIR = DATA_DIR / "chunks"
AUDIO_DIR = DATA_DIR / "audio"
TRANSCRIPTS_DIR = DATA_DIR / "transcripts"
HIGHLIGHTS_DIR = DATA_DIR / "highlights"
OUTPUT_DIR = DATA_DIR / "output"

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
# Core Processing Configuration (Phase 1)
# ─────────────────────────────────────────────

# Chunking
CHUNK_DURATION_SECONDS = 45
AUDIO_SAMPLE_RATE = 16000

# Audio analysis
SPIKE_THRESHOLD = 1.5
SILENCE_RMS_THRESHOLD = 1e-4

# Whisper
WHISPER_MODEL_NAME = "base"

# Phase 1 scoring
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


# ─────────────────────────────────────────────
# Twitch – VOD & Chat Paths
# ─────────────────────────────────────────────

TWITCH_DIR = DATA_DIR / "twitch"
TWITCH_VOD_DIR = TWITCH_DIR / "vods"
TWITCH_META_DIR = TWITCH_DIR / "metadata"

TWITCH_CHAT_DIR = TWITCH_DIR / "chat"
TWITCH_CHAT_RAW_DIR = TWITCH_CHAT_DIR / "raw"
TWITCH_CHAT_NORMALIZED_DIR = TWITCH_CHAT_DIR / "normalized"
TWITCH_CHAT_TEXT_DIR = TWITCH_CHAT_DIR / "normalized_text"
TWITCH_CHAT_USERLESS_DIR = TWITCH_CHAT_DIR / "normalized_text_userless"
TWITCH_CHAT_EMOTES_DIR = TWITCH_CHAT_DIR / "emotes"
TWITCH_CHAT_CLEAN_DIR = TWITCH_CHAT_DIR / "clean"

for directory in (
    TWITCH_DIR,
    TWITCH_VOD_DIR,
    TWITCH_META_DIR,
    TWITCH_CHAT_DIR,
    TWITCH_CHAT_RAW_DIR,
    TWITCH_CHAT_NORMALIZED_DIR,
    TWITCH_CHAT_TEXT_DIR,
    TWITCH_CHAT_USERLESS_DIR,
    TWITCH_CHAT_EMOTES_DIR,
    TWITCH_CHAT_CLEAN_DIR,
):
    directory.mkdir(parents=True, exist_ok=True)

TWITCH_DOWNLOADER_PATH = INTERNAL_DIR / "tools" / "TwitchDownloaderCLI.exe"
YT_DLP_PATH = INTERNAL_DIR / "tools" / "yt-dlp.exe"


# ─────────────────────────────────────────────
# Chat Metrics & Alignment
# ─────────────────────────────────────────────

CHAT_METRICS_DIR = DATA_DIR / "chat" / "metrics"
CHAT_METRICS_DIR.mkdir(parents=True, exist_ok=True)

CHAT_TO_VIDEO_OFFSET_SECONDS = 5


# ─────────────────────────────────────────────
# Chat Activity & Spike Detection
# ─────────────────────────────────────────────

CHAT_BASELINE_WINDOW_SECONDS = 30
CHAT_SPIKE_RATIO_THRESHOLD = 1.3
CHAT_MIN_BASELINE = 0.1


# ─────────────────────────────────────────────
# Chat Scoring Weights
# ─────────────────────────────────────────────

CHAT_ACTIVITY_WEIGHT = 0.05
CHAT_EMOTE_WEIGHT = 0.55
CHAT_KEYWORD_WEIGHT = 0.40

KEYWORD_SCORE_SCALE = 0.15
EMOTE_SCORE_SCALE = 0.25


# ─────────────────────────────────────────────
# Noise Suppression (Small Chats)
# ─────────────────────────────────────────────

MIN_CHAT_MESSAGES_PER_CHUNK = 3
MIN_CHAT_ACTIVE_SECONDS_PER_CHUNK = 2


# ─────────────────────────────────────────────
# False-Positive Filtering Thresholds
# ─────────────────────────────────────────────

PHASE1_STRONG_THRESHOLD = HIGHLIGHT_THRESHOLD + 0.1
CHAT_STRONG_THRESHOLD = 0.15
TEXT_STRONG_THRESHOLD = 0.2


# Chat score smoothing
CHAT_SMOOTHING_WINDOW_SECONDS = 3

TIMELINE_PATH = OUTPUT_DIR / "timeline.txt"


#presets
PRESETS_DIR = DATA_DIR / "presets"
PRESETS_DIR.mkdir(parents=True, exist_ok=True)


