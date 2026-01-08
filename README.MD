# Phase 3 Scope & Assumptions — Creator Publishing & Editing Layer

This document defines the **locked scope, assumptions, design constraints, and success criteria** for Phase 3 of the VOD Highlight Engine.

Phase 3 exists to transform automatically generated highlights into **publish-ready content** inside the application, without requiring external video editors.

Phase 3 builds on Phases 1 and 2.  
Phase 1 and Phase 2 functionality **must continue to work independently**.

Any feature not explicitly listed here is **out of scope** for Phase 3.

---

## 1. Phase 3 Goal

Enable creators to go from:

> **VOD → Highlights → Platform-Ready Video**

inside a single local application, with minimal manual editing.

Phase 3 focuses on:
- editing highlight timelines
- preparing content for social platforms
- adding captions and branding
- exporting final videos

Phase 3 does **not** attempt to replace professional NLE software.

---

## 2. Core Principle

> **Phases 1 and 2 decide *what* matters.  
Phase 3 decides *how it is published*.**

Phase 3 does not influence highlight detection logic.  
It operates strictly on **already-selected highlights**.

---

## 3. Definition of “Creator Publishing”

Creator publishing is defined as the ability to:

- review and edit automatically generated highlights
- make lightweight, clip-level adjustments
- apply standardized presentation layers
- export in formats optimized for social platforms

This is a **workflow acceleration layer**, not a creative editing environment.

---

## 4. Editable Highlight Timeline

Phase 3 introduces an **editable timeline** abstraction.

Supported operations:

- Enable / disable individual highlight clips
- Trim clip start and end boundaries
- Reorder clips in final output

Constraints:

- No transitions
- No keyframes
- No multi-track video
- No compositing of multiple video sources

Edits are **deterministic**, persisted to disk, and fully inspectable.

---

## 5. Captioning Model

Phase 3 supports **auto-generated captions** based on existing speech transcripts.

Assumptions:

- Sentence-level captions only
- Captions are burned into the video (no subtitle files in Phase 3)
- Caption styling is limited to:
  - font
  - size
  - position
- Captions are optional and user-controlled

Captions are treated as a **presentation layer**, not a scoring signal.

---

## 6. Platform Formatting & Aspect Ratios

Phase 3 supports export to common social video formats:

- 16:9 — YouTube
- 9:16 — TikTok, YouTube Shorts, Instagram Reels
- 1:1 — Instagram

Assumptions:

- Video reframing uses cropping or padding
- No AI-based reframing or subject tracking
- Safe zones for captions and branding are respected
- Multiple formats may be exported from the same highlight set

---

## 7. Branding & Overlays

Phase 3 supports lightweight branding:

- Static logo overlays (PNG)
- Simple text overlays (creator name, handle)

Constraints:

- No animations
- No transitions
- No motion graphics
- No per-frame effects

Branding is optional, deterministic, and controlled through presets.

---

## 8. Export Model

Phase 3 introduces **export presets** that define:

- platform format
- aspect ratio
- caption style
- branding options
- encoding settings

Exports must be:

- deterministic
- reproducible
- offline
- free of proprietary formats

Outputs are standard video files ready for upload.

---

## 9. Data Handling

- All edits are stored locally
- No cloud storage
- No user accounts
- No telemetry or analytics
- No automatic uploading to platforms

User content remains fully under local control.

---

## 10. Technical Assumptions

- CPU-only execution is acceptable
- FFmpeg remains the encoding backend
- Export runtime may increase vs Phase 2
- No paid APIs
- No cloud inference
- No machine learning models
- Deterministic outputs are required

---

## 11. Explicitly Out of Scope (Phase 3)

The following features are intentionally excluded:

- Full multi-track timeline editing
- Transitions, effects, or color grading
- Motion graphics or animations
- Keyframing
- Live streaming support
- Cloud rendering or cloud storage
- Auto-uploading to platforms
- Monetization or creator marketplaces
- Vision / facecam analysis
- ML-based clip ranking or editing
- Collaboration or shared projects

If a feature is not listed as in-scope, it does not exist in Phase 3.

---

## 12. Success Criteria (User-Level)

Phase 3 is considered successful if:

> A creator can take a Twitch VOD and publish a platform-ready highlight video directly from the application, with significantly less manual editing than traditional workflows.

Success must be:

- measurable (editing time reduced by **>50%**)
- observable (clear workflow improvement)
- explainable (no black-box behavior)
- repeatable (deterministic exports)

Creative perfection is not required.  
Speed, clarity, and control are.

---

## 13. Architectural Outcome

After Phase 3, the system provides:

- Highlight detection (Phase 1)
- Stream context awareness (Phase 2)
- Creator publishing & editing (Phase 3)

Resulting in a complete, offline pipeline:

**VOD → Highlights → Publish-Ready Video**

inside a single application, without cloud dependencies or opaque automation.

---

## Notes

Phase 3 deliberately avoids:
- AI editing
- automated ranking
- creative effects

These belong to future phases once user feedback and labeled data exist.

Phase 3 is about **empowering creators to publish faster**, not replacing professional editors.
