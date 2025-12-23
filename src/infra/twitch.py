import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from processing.chat.timestamp_normalizer import normalize_chat_timestamps
from processing.chat.text_normalizer import normalize_chat_text
from processing.chat.username_stripper import strip_usernames
from processing.chat.emote_extractor import extract_emotes
from processing.chat.message_filter import filter_chat_messages
from processing.chat.final_chat_export import export_final_chat

from infra.config import (
    TWITCH_DIR,
    TWITCH_VOD_DIR,
    TWITCH_META_DIR,
    INPUT_DIR,
    TWITCH_CHAT_RAW_DIR,
    TWITCH_DOWNLOADER_PATH,
)

TWITCH_VOD_URL_RE = re.compile(r"(?:twitch\.tv/videos/)(\d+)")


# ─────────────────────────────────────────────
# Data structures
# ─────────────────────────────────────────────

@dataclass
class TwitchVODMetadata:
    vod_id: str
    duration_seconds: int
    created_at: str
    local_video_path: Path


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _ensure_dirs():
    for d in (
        TWITCH_DIR,
        TWITCH_VOD_DIR,
        TWITCH_META_DIR,
        TWITCH_CHAT_RAW_DIR,
    ):
        d.mkdir(parents=True, exist_ok=True)


def _extract_vod_id(vod_url: str) -> str:
    match = TWITCH_VOD_URL_RE.search(vod_url)
    if not match:
        raise ValueError("Invalid Twitch VOD URL")
    return match.group(1)


def _run_yt_dlp(args: list[str], logger) -> str:
    """
    Runs yt-dlp and returns stdout.
    Progress is streamed directly to console.
    """
    logger.info("Running yt-dlp")

    result = subprocess.run(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        logger.error(result.stderr)
        raise RuntimeError("yt-dlp failed")

    return result.stdout


# ─────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────

def resolve_twitch_vod(vod_url: str, logger) -> TwitchVODMetadata:
    """
    Phase 2 – Day 16
    - Resolve Twitch VOD
    - Fetch metadata
    - Download video
    - Download chat replay
    """

    _ensure_dirs()

    vod_id = _extract_vod_id(vod_url)
    logger.info("Resolved Twitch VOD ID: %s", vod_id)

    meta_path = TWITCH_META_DIR / f"{vod_id}.json"
    video_path = TWITCH_VOD_DIR / f"{vod_id}.mp4"

    # ─── Fetch metadata ───────────────────────
    if meta_path.exists():
        logger.info("Using cached Twitch metadata")
        meta = json.loads(meta_path.read_text())
    else:
        logger.info("Fetching Twitch VOD metadata")
        output = _run_yt_dlp(
            [
                "yt-dlp",
                "--dump-json",
                "--skip-download",
                vod_url,
            ],
            logger,
        )
        meta = json.loads(output)
        meta_path.write_text(json.dumps(meta, indent=2))

    duration_seconds = int(meta["duration"])
    created_at = meta.get("upload_date", "unknown")

    # ─── Download video ───────────────────────
    if not video_path.exists():
        logger.info("Downloading Twitch VOD")
        _run_yt_dlp(
            [
                "yt-dlp",
                "-f",
                "best[ext=mp4]/best",
                "-o",
                str(video_path),
                vod_url,
            ],
            logger,
        )
    else:
        logger.info("Using cached Twitch VOD video")

    # ─── Copy into INPUT_DIR for pipeline ─────
    input_video_path = INPUT_DIR / video_path.name
    if not input_video_path.exists():
        input_video_path.write_bytes(video_path.read_bytes())

    # ─── Download chat replay ─────────────────
    download_twitch_chat(vod_id, logger)
    normalize_chat_timestamps(vod_id, logger)
    normalize_chat_text(vod_id, logger)
    strip_usernames(vod_id, logger)
    extract_emotes(vod_id, logger)
    filter_chat_messages(vod_id, logger)

    # Final canonical export
    export_final_chat(vod_id, logger)

    return TwitchVODMetadata(
        vod_id=vod_id,
        duration_seconds=duration_seconds,
        created_at=created_at,
        local_video_path=input_video_path,
    )


def download_twitch_chat(vod_id: str, logger) -> Path:
    """
    Downloads raw Twitch chat replay JSON.
    """

    output_path = TWITCH_CHAT_RAW_DIR / f"{vod_id}.json"

    if output_path.exists():
        logger.info("Using cached Twitch chat replay")
        return output_path

    logger.info("Downloading Twitch chat replay")

    cmd = [
        str(TWITCH_DOWNLOADER_PATH),
        "-m", "ChatDownload",
        "--id", vod_id,
        "--output", str(output_path),
    ]

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        logger.error(result.stderr)
        raise RuntimeError("Failed to download Twitch chat replay")

    return output_path
