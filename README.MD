# Phase 1 Scope & Assumptions — VOD Highlight Engine

This document defines the **locked scope, assumptions, and success criteria** for Phase 1 of the VOD Highlight Engine.

Phase 1 exists to prove core value:
> Convert long-form VODs (1–4 hours) into a watchable highlight video using local audio and speech signals only.

Any feature not explicitly listed here is **out of scope** for Phase 1.

---

## 1. Phase 1 Goal

Produce a **local Windows desktop application** that:
- Accepts a long-form video file
- Automatically detects key moments
- Outputs a single stitched highlight video
- Runs without cloud services or paid APIs

This phase prioritizes **correctness and usefulness**, not polish or speed.

---

## 2. Definition of a “Highlight”

A highlight is a video segment that meets **one or more measurable criteria**, with higher confidence when multiple criteria are met.

### 2.1 Audio-Based Signals (Primary)

Audio is the strongest Phase 1 signal.

A segment is considered a highlight candidate if:

- RMS audio energy exceeds **1.8× the rolling average**, OR
- Peak amplitude exceeds the **90th percentile** of the video’s audio levels

These signals capture:
- Excitement
- Screaming
- Rage
- High emotional intensity

---

### 2.2 Speech-Based Signals (Secondary)

Speech is derived from local Whisper transcription.

A segment receives a text score boost if it contains keywords or phrases indicating intensity.

#### Keyword Categories (Initial)

**Hype / Success**
- “let’s go”
- “no way”
- “holy”
- “that’s insane”
- “we did it”

**Failure / Chaos**
- “what just happened”
- “are you kidding me”
- “noooo”
- “I’m throwing”

**General Intensity**
- Profanity (configurable list)
- Repeated exclamations

Keyword lists are expected to evolve, but the **mechanism is fixed**.

---

## 3. Chunking Assumptions

- Fixed chunk duration: **45 seconds**
- No overlap between chunks
- Chunking is deterministic and repeatable
- Chunking is done before any analysis

Rationale:
- Works well with Whisper
- Limits memory usage
- Simplifies scoring and merging logic

---

## 4. Scoring Model (Phase 1)

Each chunk receives a total score based on weighted signals:

```
total_score =
(audio_score * 0.6)

(text_score * 0.4)
```

Where:
- `audio_score` ∈ [0, 10]
- `text_score` ∈ [0, 10]

### Highlight Threshold

- A chunk is considered a highlight if:
```
total_score ≥ 6.0
```


Thresholds are tunable, but Phase 1 uses fixed values.

---

## 5. Highlight Refinement Rules

To ensure watchable output:

- Minimum highlight duration: **8 seconds**
- Maximum single clip duration: **60 seconds**
- Highlight segments within **10 seconds** of each other are merged
- Buffer time is added before and after highlights

This avoids:
- Micro-clips
- Abrupt cuts
- Overlong, boring segments

---

## 6. Output Definition

Phase 1 produces:

- A **single stitched highlight video**
- Chronological order
- No transitions
- No overlays
- No burned-in captions

Filename format:
```
<original_filename>_highlights.mp4
```


The goal is signal validation, not presentation polish.

---

## 7. Technical Assumptions

- Processing is fully local
- CPU-only execution is acceptable
- Runtime may be equal to or slower than real-time
- GPU acceleration is optional, not required
- FFmpeg is used for all video operations
- Whisper runs locally (no API usage)

---

## 8. Explicitly Out of Scope (Phase 1)

The following are **intentionally excluded** from Phase 1:

- Twitch API ingestion
- Chat analysis
- Emote detection
- Facecam emotion analysis
- Visual or game-event detection
- Live stream processing
- Cloud inference
- User accounts or authentication
- Monetization or licensing
- Advanced UI/UX polish

If a feature is not listed as in-scope, it does not exist in Phase 1.

---

## 9. Success Criteria (User-Level)

Phase 1 is considered successful if:

> A streamer can provide a 1–4 hour VOD, leave the application running, and return to a watchable highlight video containing the most exciting moments.

The output does not need to be perfect or viral—only **consistently useful**.

---

## 10. Change Policy

- This document is **locked for Phase 1**
- Changes require explicit intent and documentation
- New features are deferred to later phases

This protects development velocity and prevents scope creep.

---


