# Phase 2 — Stream Context Awareness

**Goal:** Improve highlight accuracy using stream-native signals  
**Duration:** 3–5 weeks  
**Target User:** Early Twitch streamers (small–mid audience)

---

## Phase 2 Guiding Principles

- ❌ No real-time processing (VOD-only)
- ❌ No ML chat sentiment models (rule-based first)
- ❌ No vision / facecam analysis
- ❌ No paid APIs
- ❌ No multi-platform support (Twitch only)
- ✅ Deterministic, inspectable scoring
- ✅ Additive to Phase 1 (Phase 1 must remain fully functional)

---

## Day 15 — Scope Lock & Signal Definition (No Code)

- [x] Define “chat spike”
  - [x] Messages-per-second threshold
  - [x] Spike relative to rolling baseline
- [x] Define emote flood detection
  - [x] % of messages containing emotes
  - [x] Repeated identical emotes
- [x] Define chat keyword list
  - [x] Examples: “OMG”, “NO WAY”, “CLIP IT”
- [x] Define how chat affects highlights
  - [x] Additive score vs multiplier
- [x] Decide chat-to-video time alignment tolerance (± seconds)
- [x] Document assumptions in README

---

## Day 16 — Twitch VOD Metadata & Chat Acquisition

- [x] Accept Twitch VOD URL as input
- [x] Resolve VOD ID
- [x] Validate VOD duration
- [x] Download chat replay (offline)
- [x] Store raw chat logs
- [x] Handle missing / expired VODs
- [x] CLI flag: `--twitch-vod <url>`

---

## Day 17 — Chat Log Normalization

- [ ] Convert chat timestamps → seconds from VOD start
- [ ] Normalize message text (lowercase, trim)
- [ ] Strip usernames / IDs
- [ ] Extract emotes as tokens
- [ ] Filter empty / spam messages
- [ ] Save normalized output to `data/chat/normalized.json`

---

## Day 18 — Chat Activity Metrics

- [ ] Messages per second computed
- [ ] Rolling average baseline
- [ ] Spike detection implemented
- [ ] Spike metadata stored:
  - timestamp
  - magnitude
- [ ] Debug metrics logged

---

## Day 19 — Emote Flood Detection

- [ ] Emote density per second
- [ ] Repeated-emote detection
- [ ] Configure hype emotes
- [ ] Normalize emote score
- [ ] Persist emote scoring metadata

---

## Day 20 — Chat Keyword & Phrase Scoring

- [ ] Define chat keyword list
- [ ] Count keyword hits per time window
- [ ] Normalize keyword score
- [ ] Keep chat keywords separate from speech keywords
- [ ] Store keyword scoring output

---

## Day 21 — Chat Score Aggregation

- [ ] Combine:
  - chat activity score
  - emote score
  - keyword score
- [ ] Produce final chat score per second
- [ ] Apply rolling smoothing
- [ ] Export `chat_scores.json`

---

## Day 22 — Chat ↔ Video Time Alignment

- [ ] Align chat timeline to video timeline
- [ ] Configurable chat delay / offset
- [ ] Handle truncated or partial VODs
- [ ] Validate alignment on real Twitch VODs

---

## Day 23 — Chat-Weighted Highlight Scoring

- [ ] Preserve Phase 1 score as baseline
- [ ] Integrate chat score
- [ ] Expose chat weight in config
- [ ] Enable/disable chat influence
- [ ] Log combined scores per chunk

---

## Day 24 — Highlight Selection Refinement

- [ ] Allow chat-boosted highlights
- [ ] Optional chat-only highlights
- [ ] Noise suppression for small chats
- [ ] False-positive filtering

---

## Day 25 — Timeline Visualization (Minimal)

- [ ] Simple timeline view (CLI or UI)
- [ ] Overlay:
  - audio score
  - speech score
  - chat score
- [ ] Inspectable / clickable moments
- [ ] Debug-focused (not polished UI)

---

## Day 26 — UX & Controls

- [ ] Toggle chat influence on/off
- [ ] Adjust chat weight
- [ ] Show why a clip was selected
- [ ] Save/load scoring presets

---

## Day 27 — Stability & Long-VOD Testing

- [ ] Test 1–4 hour Twitch VODs
- [ ] Test small chats (<10 viewers)
- [ ] Test medium chats (50–200 viewers)
- [ ] Verify memory stability
- [ ] Ensure acceptable runtime

---

## Phase 2 Exit Criteria

- [ ] Chat spikes reliably correlate with hype moments
- [ ] Fewer false positives than Phase 1
- [ ] User can explain *why* a clip was chosen
- [ ] Phase 1 pipeline works independently
- [ ] No cloud dependencies
- [ ] Deterministic, repeatable results

---

## Architectural Outcome After Phase 2

- Three independent signals:
  - Audio
  - Speech
  - Chat
- Transparent, explainable scoring
- Debuggable highlight timeline
- Strong foundation for Phase 3 (vision, ML ranking)

---

## Notes

Rule-based chat analysis is sufficient for Phase 2.  
Machine learning belongs in Phase 3, once labeled data and user feedback exist.
