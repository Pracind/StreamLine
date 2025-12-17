# Phase 1 — VOD Highlight Engine
End Goal: Local Windows application that converts long-form VODs into highlight videos using audio + speech signals.

---

## Day 0 — Scope Lock (No Code)

- [x] Define “highlight” in measurable terms
  - [x] Audio spike threshold (RMS audio energy exceeds 1.8× the rolling average, Peak amplitude exceeds 90th percentile of the video’s audio)
  - [x] Keyword / phrase triggers (“let’s go” “no way” “holy” “that’s insane” “we did it”)
  - [x] Minimum clip duration (8 seconds - 60 seconds)
- [x] Decide fixed chunk duration (45 seconds)
- [x] Decide output format (single highlight video)
- [x] Explicitly defer:
  - [x] Chat analysis
  - [x] Vision / facecam
  - [x] Cloud inference
- [x] Write assumptions in README

---

## Day 1 — Environment & Project Setup

- [x] Python 3.11 installed (do not use 3.12)
- [x] .venv created with py -3.11
- [x] Virtual environment activates cleanly
- [x] pip, setuptools, wheel upgraded
- [x] FFmpeg installed and in PATH
- [x] Project root structure created
- [x] requirements.txt created
- [x] Dependencies install without errors
- [x] src/main.py sanity check passes
- [x] Checklist committed to repo

---

## Day 2 — Deterministic Video Chunking

- [ ] Input video loaded from data/input/
- [ ] Video split into fixed-length chunks
- [ ] No re-encoding artifacts
- [ ] Chunk filenames are sequential and deterministic
- [ ] Chunk metadata written to JSON
- [ ] All chunks play independently
- [ ] Multi-hour video tested

---

## Day 3 — Audio Extraction & Normalization

- [ ] Audio extracted from each chunk
- [ ] WAV format used consistently
- [ ] Sample rate standardized
- [ ] Audio duration matches video chunk
- [ ] Files stored in data/audio/
- [ ] Extraction errors handled gracefully

---

## Day 4 — Audio Intensity Scoring

- [ ] RMS energy calculated per chunk
- [ ] Volume spikes detected
- [ ] Silence handled correctly
- [ ] Audio score normalized
- [ ] Audio scores stored in metadata

---

## Day 5 — Speech-to-Text (Whisper)

- [ ] Whisper model integrated (local)
- [ ] Transcription cached per chunk
- [ ] Timestamps preserved
- [ ] Long videos complete without crashes
- [ ] CPU-only execution confirmed
- [ ] Transcription errors handled

---

## Day 6 — Text-Based Scoring

- [ ] Keyword list defined
- [ ] Keyword hits counted per chunk
- [ ] Optional sentiment score implemented
- [ ] Text score normalized
- [ ] Text score merged with audio metadata

---

## Day 7 — Scoring Engine & Highlight Selection

- [ ] Weighted scoring formula defined
- [ ] Audio + text scores combined
- [ ] Highlight threshold defined
- [ ] Highlight chunks flagged
- [ ] Scores logged for tuning

---

## Day 8 — Highlight Refinement

- [ ] Adjacent highlights merged
- [ ] Buffer time added before/after clips
- [ ] Clips below minimum duration removed
- [ ] Final highlight timeline produced

---

## Day 9 — Clip Extraction

- [ ] Highlight segments extracted with FFmpeg
- [ ] No A/V desync
- [ ] Sequential clip naming
- [ ] Clips stored in data/output/clips/

---

## Day 10 — Final Highlight Video Assembly

- [ ] Clips concatenated in correct order
- [ ] Final video encoded
- [ ] Playback verified
- [ ] File size reasonable
- [ ] Export completes unattended

---

## Day 11 — CLI Interface

- [ ] Single command execution supported
- [ ] Input path configurable
- [ ] Progress feedback shown
- [ ] Errors surfaced cleanly
- [ ] Repeat runs supported

---

## Day 12 — Performance & Stability Pass

- [ ] Chunk-level progress logging
- [ ] Partial progress resumable
- [ ] Temporary files cleaned up
- [ ] Memory usage acceptable
- [ ] Runtime documented

---

## Day 13 — Minimal Desktop UI

- [ ] PySide6 window created
- [ ] File picker works
- [ ] Start button triggers pipeline
- [ ] Progress bar updates
- [ ] App remains responsive

---

## Day 14 — Packaging & Distribution

- [ ] PyInstaller configuration created
- [ ] .exe built successfully
- [ ] FFmpeg bundled
- [ ] App runs on clean machine
- [ ] Basic user instructions written

---

## Phase 1 Exit Criteria

- [ ] 1–4 hour VOD → highlight video
- [ ] No cloud dependencies
- [ ] No paid APIs
- [ ] Repeatable results
- [ ] Foundation ready for Phase 2
