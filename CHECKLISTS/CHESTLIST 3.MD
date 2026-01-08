# Phase 3 — Creator Publishing & Editing Layer

**Duration:** 4–6 weeks (Target: 6 weeks)  
**Primary User:** Growth-focused creators  
**Core Metric:** Editing time reduced by **>50%**  
**Design Philosophy:** Publish fast, not replace professional NLEs

---

## Purpose

Transform automatically detected highlights into **publish-ready content** inside the app.

Creators should be able to:
- Edit highlights
- Add captions
- Apply branding
- Export for YouTube, Shorts, TikTok, and Reels  
…without opening Premiere, DaVinci, or CapCut.

---

## Capabilities

- Editable highlight timeline
- Manual clip trimming
- Auto-captions
- Aspect-ratio presets
- Branding overlays
- Export presets

---

## Non-Goals

- ❌ Full multi-track timeline editing
- ❌ Transitions / effects / color grading
- ❌ Cloud rendering or paid APIs
- ❌ Replacing Premiere / DaVinci

---

## Phase 3 Guiding Principles

- Deterministic, inspectable exports
- Offline-first
- Clip-based editing (not full timelines)
- Minimal UI, maximum leverage
- Phase 1 & 2 must remain fully functional

---

# Week 1 — Editable Timeline & Clip Control

## Day 1 — Scope Lock (No Code)

- [ ] Define “editable timeline”:
  - [ ] Enable/disable clips
  - [ ] Start/end trimming
  - [ ] Clip reordering
- [ ] Lock non-goals:
  - [ ] No transitions
  - [ ] No multi-track video
- [ ] Define UX surface:
  - [ ] Table-based timeline editor
- [ ] Update README assumptions

---

## Day 2 — Timeline Data Model (v2)

- [ ] Version timeline schema
- [ ] Add fields:
  - [ ] `enabled: bool`
  - [ ] `trim_start_offset`
  - [ ] `trim_end_offset`
  - [ ] `order_index`
- [ ] Backward compatibility with Phase 2 timelines
- [ ] Unit tests for load/save

---

## Day 3 — Editable Timeline UI

- [ ] Checkbox: enable/disable clip
- [ ] Editable trim fields
- [ ] Reorder buttons (↑ / ↓)
- [ ] Live validation:
  - [ ] No negative durations
  - [ ] Enforce minimum clip length
- [ ] Persist edits to disk

---

## Day 4 — Manual Clip Trimming Engine

- [ ] Apply trim offsets during FFmpeg extraction
- [ ] Verify:
  - [ ] No A/V desync
  - [ ] Accurate boundaries
- [ ] Regression tests:
  - [ ] No trims (baseline)
  - [ ] Aggressive trims

---

## Day 5 — Selective Export

- [ ] Skip disabled clips during:
  - [ ] Concatenation
  - [ ] Final export
- [ ] UI feedback:
  - [ ] Active clip count
- [ ] Guard against empty exports

---

## Day 6 — Timeline Preview UX

- [ ] “Open Clip”
- [ ] “Open Final Video”
- [ ] Optional: “Play From Here”
- [ ] Confirm UI remains responsive

---

## Day 7 — Week 1 Stabilization

- [ ] Test:
  - [ ] 1-hour VOD
  - [ ] 3-hour VOD
- [ ] Validate:
  - [ ] Timeline persistence
  - [ ] Correct clip ordering
- [ ] Refactor timeline UI
- [ ] Documentation update

---

# Week 2 — Auto-Captions

## Day 8 — Caption Scope Lock

- [ ] Sentence-level captions (not word-level)
- [ ] Burn-in captions (no SRT yet)
- [ ] Define:
  - [ ] Max line length
  - [ ] Wrapping rules
  - [ ] Placement (bottom center)
- [ ] Choose default font + size

---

## Day 9 — Caption Data Pipeline

- [ ] Extract Whisper timestamps per clip
- [ ] Group words into sentences
- [ ] Normalize:
  - [ ] Capitalization
  - [ ] Remove filler
- [ ] Store caption segments per clip

---

## Day 10 — FFmpeg Caption Rendering

- [ ] Implement `drawtext` filter
- [ ] Ensure:
  - [ ] Unicode-safe
  - [ ] Long text wraps correctly
- [ ] Validate performance

---

## Day 11 — Caption Controls (UI)

- [ ] Toggle captions on/off
- [ ] Sliders:
  - [ ] Font size
  - [ ] Vertical position
- [ ] Persist caption preferences

---

## Day 12 — Caption QA

- [ ] Test:
  - [ ] Fast speech
  - [ ] Long pauses
  - [ ] Overlapping dialogue
- [ ] Ensure:
  - [ ] No cut-off text
  - [ ] No desync
- [ ] Optimize FFmpeg pipeline

---

## Day 13 — Caption Presets

- [ ] Presets:
  - [ ] Minimal
  - [ ] Bold
  - [ ] Subtitle
- [ ] Save/load with export presets
- [ ] Confirm Phase 2 compatibility

---

## Day 14 — Week 2 Stabilization

- [ ] Regression:
  - [ ] Phase 1 no captions
  - [ ] Phase 2 chat scoring
  - [ ] Phase 3 captions
- [ ] Performance profiling
- [ ] UX polish

---

# Week 3 — Aspect Ratios & Platform Presets

## Day 15 — Format Strategy

- [ ] Define formats:
  - [ ] 16:9 (YouTube)
  - [ ] 9:16 (Shorts, TikTok, Reels)
  - [ ] 1:1 (Instagram)
- [ ] Decide:
  - [ ] Crop vs pad
  - [ ] Safe zones
- [ ] Document transform rules

---

## Day 16 — FFmpeg Reframing Engine

- [ ] Implement:
  - [ ] Center crop
  - [ ] Letterbox
- [ ] Validate:
  - [ ] No distortion
  - [ ] Correct aspect metadata

---

## Day 17 — Multi-Format Export

- [ ] Export same highlights in multiple formats
- [ ] Directory structure:
  - [ ] `output/youtube/`
  - [ ] `output/shorts/`
- [ ] Prevent filename collisions

---

## Day 18 — UI: Format Presets

- [ ] Dropdown:
  - [ ] YouTube
  - [ ] TikTok
  - [ ] Reels
- [ ] Display:
  - [ ] Resolution
  - [ ] Aspect ratio
- [ ] Lock invalid combinations

---

## Day 19 — Captions + Aspect Ratio QA

- [ ] Ensure captions stay visible in vertical video
- [ ] Adjust safe zones
- [ ] Validate on tall previews

---

## Day 20 — Export Presets

- [ ] Save:
  - [ ] Caption style
  - [ ] Format
  - [ ] Bitrate
- [ ] One-click export
- [ ] Deterministic output verification

---

## Day 21 — Week 3 Stabilization

- [ ] Multi-format regression tests
- [ ] Encoding performance check
- [ ] Bug fixes
- [ ] Documentation update

---

# Week 4 — Branding & Creator Workflow

## Day 22 — Branding Design

- [ ] Define:
  - [ ] Logo overlay
  - [ ] Lower-third text
- [ ] Decide:
  - [ ] Static image overlay
  - [ ] Text overlay
- [ ] Non-goals:
  - [ ] Animations
  - [ ] Transitions

---

## Day 23 — FFmpeg Overlay Engine

- [ ] Image overlay
- [ ] Text overlay
- [ ] Controls:
  - [ ] Opacity
  - [ ] Padding
- [ ] Artifact-free output

---

## Day 24 — Branding UI

- [ ] Upload logo
- [ ] Text input for creator name
- [ ] Toggle branding on/off
- [ ] Persist per export preset

---

## Day 25 — Creator Workflow Polishing

- [ ] One-click:
  - [ ] “Export for TikTok”
  - [ ] “Export for YouTube”
- [ ] Progress indicators
- [ ] Prevent accidental overwrite
- [ ] Clear error reporting

---

## Day 26 — End-to-End Creator Test

- [ ] Real VOD test:
  - [ ] Generate highlights
  - [ ] Trim manually
  - [ ] Add captions
  - [ ] Apply branding
  - [ ] Export vertical + horizontal
- [ ] Measure time saved vs manual editing

---

## Day 27 — Final Stabilization

- [ ] Memory profiling
- [ ] Long export stress test
- [ ] Validate:
  - [ ] No corrupted files
  - [ ] No missing assets
- [ ] Clean logs and UI copy

---

# Phase 3 Exit Criteria

- [ ] Creators can:
  - [ ] Trim clips
  - [ ] Add captions
  - [ ] Apply branding
  - [ ] Export platform-ready videos
- [ ] Editing time reduced by **>50%**
- [ ] Phase 1 & 2 remain independent
- [ ] Offline-only
- [ ] Repeatable, deterministic exports

---

# Architectural Outcome

After Phase 3, the system becomes:

**VOD → Highlights → Publish-Ready Content**

Inside one offline application, with:
- Transparent scoring
- Editable timeline
- Creator-focused publishing tools

This is no longer just a tool.  
It is a **creator pipeline product**.

---

## Notes

This phase is intentionally:
- Minimal
- Deterministic
- High-leverage

Machine learning and vision-based ranking belong in Phase 4, once user feedback and labeled data exist.
