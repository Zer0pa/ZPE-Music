# Geogram 6 L3 Expression Follow-up Final Report

Date: 2026-04-20
Lane: `L3`
Status: final

## Claim Class

`stroke-decomposable`

## Frozen Scope

Authoritative path:

`IMCEncoder.add_music -> music/parser.py -> music/grid.py -> music/strokes.py -> music/pack.py -> IMCDecoder music block reconstruction`

Frozen base remains:

- canonical symbolic score events
- `onset_quarter`
- `duration_quarter`
- `pitch/rest`
- canonical `part`
- canonical `voice`
- per-event `program`
- supported articulation flags

Bounded Geogram 6 fiber transition:

- note-local performance onset delta
- note-local performance duration delta
- note-local velocity
- raw native surface: MusicXML note-level `attack`, `release`, and `dynamics` attributes on the same authoritative `add_music()` path

This is a real fiber only because the performance fields now ride on the same authoritative note object as the frozen score base. No second performed-note stream is needed.

## Authoritative Adopter Status

`bounded_expression_fiber_adopter`

Geogram 5's blocker was real. `temporal_codec.py` was exact but helper-leaking because it re-encoded an absolute performed-note stream. Geogram 6 fixes the kill location instead of narrating around it: score-anchored performance fields were added to the authority-native `NoteEvent -> GridNote -> MusicStroke -> pack/unpack` path.

## What Was Added

1. Authority-native note-level performance fields:
   `performance_onset_quarter_delta`, `performance_duration_quarter_delta`, and `velocity` on `NoteEvent`, with corresponding grid/stroke fields in tick units.

2. Parser support on the same raw path:
   MusicXML `attack`, `release`, and `dynamics` are now extracted directly from note elements while preserving the frozen symbolic score parse.

3. Wire support:
   music pack/unpack now carries bounded expression controls on the same stroke as the score note rather than through a second note stream.

4. Falsifier tests:
   expression roundtrip, repeated-note anchoring, tuplet-expression, and same-score-different-expression alias probes.

## Authority Metrics

Base preserved:

- `event_exact_rate_mean = 1.0`
- `note_event_exact_rate_mean = 1.0`
- `part_exact_rate_mean = 1.0`
- `rest_exact_rate_mean = 1.0`
- `articulation_exact_rate_mean = 1.0`
- base helper gap remains `-0.2`

Expression fiber added:

- `expression_event_exact_rate_mean = 1.0`
- `expression_onset_delta_exact_rate_mean = 1.0`
- `expression_duration_delta_exact_rate_mean = 1.0`
- `velocity_exact_rate_mean = 1.0`
- `performance_tuple_exact_rate_mean = 1.0`
- `expression_onset_delta_mae_mean = 0.0`
- `expression_duration_delta_mae_mean = 0.0`
- `velocity_mae_mean = 0.0`

Per-case sovereign result:

- `expressive_phrase = 1.0`
- `repeated_note_anchoring = 1.0`
- `tuplet_expression = 1.0`

The repeated-note cell matters. It was the honest candidate kill. It did not kill the route once expression lived on the same score note stroke.

## Audit-Only Proxy Metrics

- expression projection exactness mean: `1.0`
- expression mean stream word count: `45.666666666666664`

These are audit-only. They agree with the sovereign exactness results but do not clear the gate.

## Helper Leakage Result

Inherited base helper result remains:

- `exact_rate_gain_helper_minus_raw = -0.2`

Expression fiber helper comparison:

- helper route: `music/temporal_codec.py` absolute performed-note stream
- `helper_expression_exact_rate_mean = 1.0`
- `authority_expression_exact_rate_mean = 1.0`
- `exact_rate_gain_helper_minus_raw = 0.0`

Meaning:

The helper no longer has any advantage. That is the key difference from Geogram 5. Exactness is now available on the authority path itself.

## Worst-Cell Result

- `expression_event_exact_rate_min = 1.0`
- `base_event_exact_rate_min = 1.0`
- `expression_onset_delta_exact_rate_min = 1.0`
- `expression_duration_delta_exact_rate_min = 1.0`
- `velocity_exact_rate_min = 1.0`
- collapsed expression alias probes: `0/3`

Expression alias probes that no longer collapse:

- `velocity_48_vs_96`
- `attack_minus2_vs_plus2`
- `release_minus2_vs_plus2`

## Direct-Baseline Delta

- direct expression baseline exactness: `1.0`
- authority expression exactness mean: `1.0`
- delta: `0.0`

The authority path neither inflates nor loses the new fiber relative to direct object-space projection.

## Frozen Non-Claims

- no audio waveform claim
- no raw MusicXML part-name identity claim
- no continuous tempo-curve claim
- no continuous dynamics-curve claim
- no pedal or sustain-state claim
- no performer-state / interpretation-model claim

This is not "full expression." It is a bounded note-local fiber transition.

## Final Verdict

Bounded score-anchored expression fiber transition achieved.

The decisive Geogram 5 blocker was repaired on the real live path. MusicXML note-level `attack`, `release`, and `dynamics` now survive authority encode/decode exactly as note-local fiber fields over the frozen symbolic score base. This is not base inflation, and it is not helper leakage.

## Verified Scientific Learning

- Music is a strong-fit bundle lane in the bounded note-local regime.
- Repeated same-pitch notes do not force a second performed-note base when expression is attached to the authoritative score note itself.
- The right kill location was the authority-native note object and wire semantics, not a better helper route.

## Next Executable Task

If the lane widens again, the next honest targets are:

1. note-local state beyond `velocity` / `attack` / `release`
2. tempo and dynamic curves
3. pedal or sustain only if they can be attached without breaking the score-anchored fiber contract

Do not widen by reverting to an absolute performed-note base.
