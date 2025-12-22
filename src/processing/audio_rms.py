import json
from pathlib import Path

import numpy as np
import soundfile as sf

from infra.config import AUDIO_DIR, CHUNKS_DIR, SPIKE_THRESHOLD, SILENCE_RMS_THRESHOLD


def calculate_rms_energy(logger, resume: bool):
    audio_files = sorted(AUDIO_DIR.glob("chunk_*.wav"))

    if not audio_files:
        logger.error("No audio files found for RMS calculation")
        raise RuntimeError("No audio files found for RMS calculation")

    existing_rms = {}

    metadata_path = CHUNKS_DIR / "chunks.json"
    if resume and metadata_path.exists():
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
            for entry in metadata:
                if "audio_rms" in entry:
                    existing_rms[Path(entry["file"]).stem] = entry["audio_rms"]

    total = len(audio_files)
    rms_results = {}

    for idx, audio_path in enumerate(audio_files, start=1):
        stem = audio_path.stem

        # ✅ RESUME LOGIC
        if resume and stem in existing_rms:
            logger.info(
                f"RMS [{idx}/{total}] cache hit: {audio_path.name}"
            )
            rms_results[stem] = existing_rms[stem]
            continue

        logger.info(
            f"RMS [{idx}/{total}] calculating {audio_path.name}"
        )

        try:
            audio_data, _ = sf.read(audio_path)

            if audio_data.ndim > 1:
                audio_data = np.mean(audio_data, axis=1)

            rms = np.sqrt(np.mean(np.square(audio_data)))
            rms_results[stem] = float(rms)

        except Exception as e:
            logger.exception(f"Failed RMS calculation for {audio_path.name}")
            raise RuntimeError(
                f"RMS calculation failed for {audio_path.name}"
            ) from e

    return rms_results



def write_rms_to_metadata(rms_results):
    metadata_path = CHUNKS_DIR / "chunks.json"

    if not metadata_path.exists():
        raise RuntimeError("chunks.json not found.")

    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    for entry in metadata:
        chunk_stem = Path(entry["file"]).stem
        entry["audio_rms"] = rms_results.get(chunk_stem, 0.0)

    metadata = detect_volume_spikes(metadata)
    metadata = normalize_audio_scores(metadata)

    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)



def detect_volume_spikes(metadata):
    rms_values = np.array(
        [entry.get("audio_rms", 0.0) for entry in metadata]
    )

    if len(rms_values) == 0:
        return metadata

    median_rms = np.median(rms_values)

    if median_rms == 0:
        median_rms = 1e-9

    for entry in metadata:
        rms = entry.get("audio_rms", 0.0)

        # Silence handling
        if rms < SILENCE_RMS_THRESHOLD:
            entry["is_silent"] = True
            entry["audio_spike_score"] = 0.0
            entry["is_volume_spike"] = False
            continue

        entry["is_silent"] = False

        spike_score = rms / median_rms

        entry["audio_spike_score"] = float(spike_score)
        entry["is_volume_spike"] = bool(spike_score >= SPIKE_THRESHOLD)

    return metadata



def normalize_audio_scores(metadata):
    # Collect spike scores for non-silent chunks
    spike_scores = [
        entry["audio_spike_score"]
        for entry in metadata
        if not entry.get("is_silent", False)
    ]

    if not spike_scores:
        # All chunks silent
        for entry in metadata:
            entry["audio_score"] = 0.0
        return metadata

    min_score = min(spike_scores)
    max_score = max(spike_scores)

    for entry in metadata:
        if entry.get("is_silent", False):
            entry["audio_score"] = 0.0
            continue

        if max_score == min_score:
            # Avoid division by zero if all scores are identical
            entry["audio_score"] = 0.0
        else:
            normalized = (
                (entry["audio_spike_score"] - min_score)
                / (max_score - min_score)
            )
            entry["audio_score"] = float(normalized)

    return metadata