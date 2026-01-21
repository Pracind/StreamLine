"""
Twitch VOD resolution, download, and chat replay ingestion.

This module is responsible for:
- Resolving a Twitch VOD URL to a concrete VOD ID
- Fetching and caching VOD metadata
- Downloading the VOD video file
- Downloading, normalizing, and exporting chat replay data

It serves as the Phase 2 entry point for Twitch-based processing.
"""

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
    YT_DLP_PATH,
)

# Regex for extracting numeric VOD IDs from Twitch VOD URLs
TWITCH_VOD_URL_RE = re.compile(r"(?:twitch\.tv/videos/)(\d+)")


# ─────────────────────────────────────────────
# Data structures
# ─────────────────────────────────────────────

@dataclass
class TwitchVODMetadata:
    """
    Canonical metadata returned after resolving a Twitch VOD.
    """
    vod_id: str
    duration_seconds: int
    created_at: str
    local_video_path: Path


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _ensure_dirs():
    """
    Ensure all Twitch-related directories exist.
    """
    for d in (
        TWITCH_DIR,
        TWITCH_VOD_DIR,
        TWITCH_META_DIR,
        TWITCH_CHAT_RAW_DIR,
    ):
        d.mkdir(parents=True, exist_ok=True)


def _extract_vod_id(vod_url: str) -> str:
    """
    Extract the numeric VOD ID from a Twitch VOD URL.

    Raises:
        ValueError: If the URL does not match the expected Twitch format.
    """
    match = TWITCH_VOD_URL_RE.search(vod_url)
    if not match:
        raise ValueError("Invalid Twitch VOD URL")
    return match.group(1)


def _run_yt_dlp(args: list[str], logger) -> str:
    """
    Run yt-dlp with real-time logging and capture combined stdout.

    This helper:
    - Resolves yt-dlp explicitly when invoked by name
    - Streams output lines directly into the application logger
    - Raises on non-zero exit codes

    Returns:
        Combined stdout output as a single string.
    """
    logger.info("Running yt-dlp: %s", " ".join(args))

    # Resolve executable explicitly
    exe = args[0]

    # If using bare "yt-dlp", ensure it exists on PATH
    if exe.lower() == "yt-dlp":
        import shutil
        resolved = shutil.which("yt-dlp")
        logger.info("Resolved yt-dlp path: %s", resolved)
        if not resolved:
            raise FileNotFoundError("yt-dlp not found on PATH inside EXE environment")
        args = [resolved] + args[1:]

    process = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )

    output_lines = []

    for line in process.stdout:
        line = line.rstrip()
        if line:
            logger.info("[yt-dlp] %s", line)
            output_lines.append(line)

    process.wait()

    logger.info("yt-dlp exited with code %d", process.returncode)

    if process.returncode != 0:
        raise RuntimeError("yt-dlp failed")

    return "\n".join(output_lines)


# ─────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────

def resolve_twitch_vod(vod_url: str, logger) -> TwitchVODMetadata:
    """
    Resolve a Twitch VOD URL and prepare it for pipeline processing.

    Responsibilities:
    - Resolve VOD ID from URL
    - Fetch and cache metadata
    - Download the VOD video if needed
    - Copy the video into INPUT_DIR for downstream processing
    - Download and normalize Twitch chat replay
    - Export the final canonical chat dataset

    Returns:
        TwitchVODMetadata describing the resolved VOD.
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
                str(YT_DLP_PATH),
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
                str(YT_DLP_PATH),
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

    # ─── Download and normalize chat replay ───
    download_twitch_chat(vod_id, logger)
    normalize_chat_timestamps(vod_id, logger)
    normalize_chat_text(vod_id, logger)
    strip_usernames(vod_id, logger)
    extract_emotes(vod_id, logger)
    filter_chat_messages(vod_id, logger)

    # Final canonical chat export
    export_final_chat(vod_id, logger)

    return TwitchVODMetadata(
        vod_id=vod_id,
        duration_seconds=duration_seconds,
        created_at=created_at,
        local_video_path=input_video_path,
    )


def download_twitch_chat(vod_id: str, logger) -> Path:
    """
    Download the raw Twitch chat replay for a given VOD.

    Uses TwitchDownloaderCLI to fetch chat messages and streams
    progress output into the application logger.

    Returns:
        Path to the downloaded raw chat JSON file.
    """
    output_path = TWITCH_CHAT_RAW_DIR / f"{vod_id}.json"

    if output_path.exists():
        logger.info("Using cached Twitch chat replay")
        return output_path

    logger.info("Downloading Twitch chat replay")

    # Verify TwitchDownloader executable
    logger.info("TwitchDownloader path: %s", TWITCH_DOWNLOADER_PATH)
    logger.info("TwitchDownloader exists: %s", TWITCH_DOWNLOADER_PATH.exists())

    if not TWITCH_DOWNLOADER_PATH.exists():
        raise FileNotFoundError(
            f"TwitchDownloaderCLI.exe not found at: {TWITCH_DOWNLOADER_PATH}"
        )

    cmd = [
        str(TWITCH_DOWNLOADER_PATH),
        "-m", "ChatDownload",
        "--id", vod_id,
        "--output", str(output_path),
    ]

    logger.info("Running: %s", " ".join(cmd))

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )

    for line in process.stdout:
        line = line.rstrip()
        if line:
            logger.info("[TwitchDownloader] %s", line)

    process.wait()

    if process.returncode != 0:
        logger.error("TwitchDownloader exited with code %d", process.returncode)
        raise RuntimeError("Failed to download Twitch chat replay")

    if not output_path.exists():
        raise RuntimeError(
            "TwitchDownloader reported success, but no chat file was created"
        )

    logger.info("Chat replay downloaded: %s", output_path)
    return output_path
