# Geogram 5 L3 Music Final Report

Date: 2026-04-20
Lane: `L3`
Status: final

## Claim Class

`stroke-decomposable`

## Frozen Scope

Base preserved on the authoritative split path:

`IMCEncoder.add_music -> music/parser.py -> music/grid.py -> music/strokes.py -> music/pack.py -> IMCDecoder music block reconstruction`

Frozen base scope:

- canonical symbolic score events
- `onset_quarter`
- `duration_quarter`
- `pitch/rest`
- canonical `part`
- canonical `voice`
- per-event `program`
- supported articulation flags

Geogram 5 fiber probe scope:

- test whether expressive performance can ride on top of the frozen score base
- do not count any route that reconstructs performance without depending on the frozen base

## Authoritative Adopter Status

Base: `preserved_bounded_adopter`

Fiber: `blocked`

The Geogram 4 bounded score adopter survives the repo split. The expression extension does not clear the fiber contract.

## Split Preservation

Proof surfaces now clear in the split workspace itself:

- `pytest` on `test_music_authority_roundtrip.py` and `test_music_authority_guardrails.py`: `6 passed`
- test helpers auto-discover the sibling `zpe-core` repo
- missing `music21` now fails loud on `add_music()` instead of silently dropping to the lossy fallback

The preservation point matters. A silent fallback would have turned an environment miss into a fake pass narrative. That guardrail is now closed.

## Authority Metrics

- `event_exact_rate_mean = 1.0`
- `note_event_exact_rate_mean = 1.0`
- `part_exact_rate_mean = 1.0`
- `rest_exact_rate_mean = 1.0`
- `articulation_exact_rate_mean = 1.0`
- `articulation_positive_recall_mean = 1.0`
- `parser_voice_capture_rate_mean = 1.0`
- `parser_program_capture_rate_mean = 1.0`
- `onset_quarter_mae_mean = 0.0`
- `duration_quarter_mae_mean = 0.0`
- `pitch_midi_mae_mean = 0.0`

Worst bounded cells remain exact:

- `simple_scale_fixture = 1.0`
- `rest_articulation = 1.0`
- `multitrack_tempo_program = 1.0`
- `voice_tagged_polyphony = 1.0`
- `tuplet_grid = 1.0`

## Audit-Only Proxy Metrics

- `mean_geometry_signature_exact_rate = 1.0`
- `mean_onset_tick_mae = 0.0`
- `mean_duration_tick_mae = 0.0`
- `mean_relative_pitch_index_mae = 0.0`
- `mean_stream_word_count = 38.0`
- `note_count_pass_rate = 1.0`

These remain audit-only. They agree with the sovereign event metrics but do not replace them.

## Helper Leakage Result

Frozen Geogram 4 helper result remains true after the split:

- `raw_authority_note_event_exact_rate_mean = 1.0`
- `helper_note_event_exact_rate_mean = 0.8`
- `helper_program_exact_rate_mean = 0.8`
- `exact_rate_gain_helper_minus_raw = -0.2`

So the shipped symbolic score adopter still has no helper advantage.

## Worst-Cell Result

- `authority_event_exact_rate_min = 1.0`
- `authority_note_event_exact_rate_min = 1.0`
- `part_exact_rate_min = 1.0`
- `rest_exact_rate_min = 1.0`
- `parser_voice_capture_rate_min = 1.0`
- `parser_program_capture_rate_min = 1.0`
- `articulation_positive_recall_min = 1.0`
- collapsed alias probes: `0/4`

## Direct-Baseline Delta

- direct baseline event exactness: `1.0`
- authority event exactness mean: `1.0`
- delta: `0.0`

The split preserved the adopter. It did not improve or degrade the frozen bounded contract.

## Expressive Fiber Probe

Candidate exact expression route tested:

`source/music/temporal_codec.py`

What it can encode exactly on synthetic expressive cases:

- performed onset in milliseconds
- performed duration in milliseconds
- velocity
- channel
- program

What the probe found:

- `overlay_event_exact_rate_mean = 1.0`
- `overlay_velocity_exact_rate_mean = 1.0`
- `overlay_alone_performance_exact_rate_mean = 1.0`

Why this is a blocker, not a win:

- the route stores absolute `pitch`
- it stores absolute `start_ms`
- it stores absolute `duration_ms`
- it stores `program`
- it does **not** store score-note identity
- `NoteEvent`, `GridNote`, and `MusicStroke` have no note-level performance fields
- the authority music pack has no expression control tags, only:
  `TIME_ANCHOR`, `PITCH_ORIGIN`, `TIME_STEP_DEN`, `PART_INDEX`, `VOICE_INDEX`, `FLAGS`, `PROGRAM`

So the current exact expressive route is a second note-stream base. It reconstructs performance without needing the frozen score. That is helper leakage, not a real fiber over the symbolic orbifold.

## Frozen Non-Claims

- no audio waveform claim
- no raw MusicXML part-name identity claim
- no tempo-change or dynamic-change exactness claim
- no expressive-performance adopter claim
- no claim that `temporal_codec` is a real score fiber

## Final Verdict

Split preservation succeeded. The bounded symbolic-score adopter remains real in `zpe-music-codec`.

The expressive-performance extension does not clear. Current exactness comes only from `temporal_codec`, and that route is helper-laundered because it re-encodes the performed note stream instead of depending on the frozen score base.

## Next Executable Task

If this lane is widened honestly, the next task is not “more exact temporal helper tests.” It is to add score-anchored performance fields and authority-pack semantics on the live path, for example:

1. note-indexed onset deltas
2. note-indexed duration deltas
3. note-indexed velocity
4. any required part/voice anchoring for repeated-note disambiguation

Only after that exists can expression be tested as a real fiber instead of a replacement base.
