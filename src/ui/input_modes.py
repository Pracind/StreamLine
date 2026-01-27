"""
Input mode definitions for UI-driven pipeline execution.

This module defines the supported input sources that the UI can pass
to the pipeline runner.
"""

from enum import Enum


class InputMode(Enum):
    """
    Enumeration of supported input modes.

    Each mode determines how the pipeline interprets the user-provided
    input value.
    """
    LOCAL = "local"            # Local video file path
    TWITCH_URL = "twitch_url"  # Full Twitch VOD URL
    TWITCH_ID = "twitch_id"    # Raw Twitch VOD ID
