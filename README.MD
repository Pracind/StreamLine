# Phase 2 Scope & Assumptions — Stream Context Awareness

This document defines the **locked scope, assumptions, and success criteria** for Phase 2 of the VOD Highlight Engine.

Phase 2 exists to improve **highlight accuracy and confidence** by incorporating **stream-native social signals**, while preserving the deterministic, local-first architecture proven in Phase 1.

Phase 2 builds on Phase 1.  
Phase 1 functionality **must continue to work independently**.

Any feature not explicitly listed here is **out of scope** for Phase 2.

---

## 1. Phase 2 Goal

Enhance highlight detection by incorporating **viewer reaction signals**, specifically:

- Twitch chat activity
- Emote usage
- Chat keyword spikes

The system should more reliably identify:
- hype moments
- clutch plays
- unexpected events
- chaotic or viral moments

without relying on cloud services, paid APIs, or machine learning models.

---

## 2. Core Principle

> **Audio + speech detect excitement.  
Chat confirms that excitement mattered to viewers.**

Chat signals do not replace Phase 1 signals — they **reinforce or suppress** them.

---

## 3. Definition of a “Chat-Driven Signal”

A chat-driven signal is any measurable pattern in viewer chat that correlates with excitement or importance.

Phase 2 recognizes three chat signal categories.

---

### 3.1 Chat Activity Spikes (Primary Chat Signal)

A chat activity spike occurs when:

- Messages-per-second exceeds a rolling baseline by a configurable multiplier, OR
- Absolute message volume crosses a minimum threshold

These spikes capture:
- sudden excitement
- surprise
- large reactions to in-game events

Small chats are handled differently than large chats (see assumptions).

---

### 3.2 Emote Floods (Secondary Chat Signal)

An emote flood occurs when:

- A high percentage of messages contain emotes, OR
- The same emote is repeated frequently in a short window

Examples:
- Pog
- PogChamp
- LUL
- KEKW
- ResidentSleeper (negative signal)

Emotes are treated as **semantic intensity markers**, not language.

---

### 3.3 Chat Keyword & Phrase Triggers (Tertiary Chat Signal)

Chat messages receive keyword-based boosts for phrases such as:

- “OMG”
- “NO WAY”
- “CLIP IT”
- “WHAT”
- “INSANE”

These keywords are **separate** from speech keywords and have independent configuration.

---

## 4. Twitch VOD Assumptions

Phase 2 supports **Twitch VODs only**.

Assumptions:
- VODs are processed offline (not live)
- Chat replay is available
- Chat timestamps can be aligned to VOD time
- Moderate delay (chat lag) is expected and compensated for

Multi-platform support is explicitly deferred.

---

## 5. Chat Data Handling

- Chat logs are downloaded once per VOD
- Chat is processed locally
- No user accounts or OAuth persistence required
- Usernames are not stored or surfaced
- Only message text, timestamp, and emotes are retained

Privacy-sensitive data is intentionally minimized.

---

## 6. Time Alignment Model

- Chat events are aligned to video time in seconds
- A configurable offset is applied to account for stream delay
- Alignment tolerance is explicitly defined (e.g. ±3 seconds)

Perfect synchronization is **not required**, but gross misalignment is unacceptable.

---

## 7. Phase 2 Scoring Model

Phase 2 introduces a **third scoring channel**:

```
total_score =
-> (audio_score * A)

-> (text_score * B)

-> (chat_score * C)
```


Where:
- `audio_score` comes from Phase 1
- `text_score` comes from Phase 1
- `chat_score` is derived from chat activity, emotes, and keywords

Weights are configurable but default to conservative values.

### Design Rules

- Chat can **boost** or **dampen** a highlight
- Chat alone may surface highlights, but only above a minimum confidence threshold
- Phase 1 signals must still be sufficient to produce highlights without chat

---

## 8. Highlight Refinement (Phase 2)

Phase 2 may:

- Boost borderline highlights when chat confirms excitement
- Suppress false positives when chat is silent
- Merge highlights reinforced by sustained chat activity

Phase 1 refinement rules still apply:
- minimum duration
- merging windows
- buffering

No visual effects or presentation changes are introduced.

---

## 9. Output Definition (Phase 2)

Phase 2 produces the **same output artifacts as Phase 1**:

- A single stitched highlight video
- Chronological order
- No transitions
- No overlays

Additional debug artifacts may be produced:
- chat score timelines
- scoring logs
- inspection views

These are for tuning and transparency, not end-user presentation.

---

## 10. Technical Assumptions

- All processing remains local
- No paid APIs
- No cloud inference
- CPU-only execution is acceptable
- Runtime may increase vs Phase 1
- Deterministic results are required
- Rule-based logic only (no ML models)

---

## 11. Explicitly Out of Scope (Phase 2)

The following are intentionally excluded:

- Live stream processing
- YouTube VODs or chat
- TikTok / Kick / YouTube Live
- Vision or facecam analysis
- Automatic clip ranking via ML
- User accounts or personalization
- Cloud sync or storage
- Auto-uploading clips
- Monetization features

If a feature is not listed as in-scope, it does not exist in Phase 2.

---

## 12. Success Criteria (User-Level)

Phase 2 is considered successful if:

> A streamer can process a Twitch VOD and receive highlight videos that more reliably reflect moments the audience actually reacted to, compared to Phase 1 alone.

Improvements should be:
- observable
- explainable
- repeatable

Perfection is not required.  
Consistency and clarity are.

---
