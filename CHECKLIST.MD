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

- [x] Input video loaded from data/input/
- [x] Video split into fixed-length chunks
- [x] No re-encoding artifacts
- [x] Chunk filenames are sequential and deterministic
- [x] Chunk metadata written to JSON
- [x] All chunks play independently
- [x] Multi-hour video tested

---

## Day 3 — Audio Extraction & Normalization

- [x] Audio extracted from each chunk
- [x] WAV format used consistently
- [x] Sample rate standardized
- [x] Audio duration matches video chunk
- [x] Files stored in data/audio/
- [x] Extraction errors handled gracefully

---

## Day 4 — Audio Intensity Scoring

- [X] RMS energy calculated per chunk
- [x] Volume spikes detected
- [x] Silence handled correctly
- [x] Audio score normalized
- [x] Audio scores stored in metadata

---

## Day 5 — Speech-to-Text (Whisper)

- [x] Whisper model integrated (local)
- [ ] Transcription cached per chunk (deferred — Phase 2)
- [x] Timestamps preserved
- [x] Long videos complete without crashes
- [x] CPU-only execution confirmed
- [x] Transcription errors handled

---

## Day 6 — Text-Based Scoring

- [x] Keyword list defined
- [x] Keyword hits counted per chunk
- [x] Optional sentiment score implemented
- [x] Text score normalized
- [x] Text score merged with audio metadata

---

## Day 7 — Scoring Engine & Highlight Selection

- [x] Weighted scoring formula defined
- [x] Audio + text scores combined
- [x] Highlight threshold defined
- [x] Highlight chunks flagged
- [x] Scores logged for tuning

---

## Day 8 — Highlight Refinement

- [x] Adjacent highlights merged
- [x] Buffer time added before/after clips
- [x] Clips below minimum duration removed
- [x] Final highlight timeline produced

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
