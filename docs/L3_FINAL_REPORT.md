# Geogram 4 L3 Music Final Report

Date: 2026-04-20
Lane: `L3`
Status: final

## Claim Class

`stroke-decomposable`

## Frozen Scope

Authoritative path tested:

`IMCEncoder.add_music -> music/parser.py -> music/grid.py -> music/strokes.py -> music/pack.py -> IMCDecoder music block reconstruction`

Bounded adopter scope:

- canonical symbolic score events
- `onset_quarter`
- `duration_quarter`
- `pitch/rest`
- canonical `part`
- canonical `voice`
- per-event `program`
- supported articulation flags

Out of scope:

- audio waveform / voice understanding
- raw MusicXML part-name identity
- tempo-change and dynamic-change exactness
- expressive performance nuance and timbre

## Authoritative Adopter Status

`bounded_adopter`

Geogram 3 was correct about the family and the kill location. The toroidal/quotient geometry was already real. The failure was the authority wire plus reconstruction, with secondary parser instability. After fixing those components, the bounded symbolic-score path now clears the authoritative gate.

## What Was Fixed

1. Parser canonicalization:
   `part` now normalizes to `P1`, `P2`, ...
   `voice` now normalizes to `V1`, `V2`, ...
   per-part MIDI program recovery was added where MusicXML exposes it.

2. Authority wire:
   `pack_music_strokes()` / `unpack_music_words()` now carry the missing sovereign fields:
   `pitch_origin`, `time_step_quarter` denominator, `part`, `voice`, rest/articulation flags, and `program`.

3. Metadata handoff:
   `IMCEncoder.add_music()` now packs `grid.metadata`, not the pre-grid parser metadata.

4. Reconstruction:
   `strokes_to_grid()` now respects decoded `time_step_quarter` instead of silently replacing it with `0.25`.

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
- multitrack source cases: `2`
- multitrack decoded cases: `2`

Per-case sovereign result:

- `simple_scale_fixture`: authority exact `1.0`, part exact `1.0`
- `rest_articulation`: authority exact `1.0`, part exact `1.0`
- `multitrack_tempo_program`: authority exact `1.0`, part exact `1.0`
- `voice_tagged_polyphony`: authority exact `1.0`, part exact `1.0`
- `tuplet_grid`: authority exact `1.0`, part exact `1.0`

## Audit-Only Proxy Metrics

- `mean_geometry_signature_exact_rate = 1.0`
- `mean_onset_tick_mae = 0.0`
- `mean_duration_tick_mae = 0.0`
- `mean_relative_pitch_index_mae = 0.0`
- `mean_stream_word_count = 38.0`
- `note_count_pass_rate = 1.0`

These are no longer the story. They simply agree with the sovereign event metrics.

## Helper Leakage Result

Helper route:

`music/temporal_codec.py` in grid-tick units, leakage-only

Summary:

- `raw_authority_note_event_exact_rate_mean = 1.0`
- `helper_note_event_exact_rate_mean = 0.8`
- `helper_program_exact_rate_mean = 0.8`
- `exact_rate_gain_helper_minus_raw = -0.2`

Meaning:

The helper route no longer recovers anything the authority path lacks. The helper advantage is gone. On the hardest bounded cell (`tuplet_grid`), the authority path is now stronger than the helper.

## Worst-Cell Result

- `authority_event_exact_rate_min = 1.0`
- `authority_note_event_exact_rate_min = 1.0`
- `part_exact_rate_min = 1.0`
- `rest_exact_rate_min = 1.0`
- `parser_voice_capture_rate_min = 1.0`
- `parser_program_capture_rate_min = 1.0`
- `articulation_positive_recall_min = 1.0`
- collapsed alias probes: `0/4`

Alias probes that no longer collapse:

- `rest_vs_note_origin`
- `plain_vs_staccato`
- `piano_vs_violin_program`
- `part_assignment_cg_vs_gc`

## Direct-Baseline Delta

- direct baseline event exactness: `1.0`
- authority event exactness mean: `1.0`
- delta: `0.0`

Projection-only isolation also now passes at `1.0`, so the decisive Geogram 3 diagnosis can be refined:

- parser was a secondary instability surface
- projection was never the kill
- reconstruction and wire semantics were the primary kill, and that kill has been repaired on the bounded scope

## Frozen Non-Claims

- no audio waveform claim
- no raw MusicXML part-name identity claim
- no tempo-change or dynamic-change exactness claim
- no expressive-performance or timbre claim

These are not hidden failures. They are explicit scope boundaries for the bounded adopter.

## Final Verdict

Bounded adopter achieved for canonical symbolic score events on the authoritative music path.

This is not universal music closure and it is not an audio claim. It is a real bounded symbolic-score codec. The authority gate now clears because the live path carries the decisive symbolic state instead of laundering it through geometry-only proxies.

## Next Executable Task

If this lane is widened in a later wave, the next honest expansion targets are:

1. tempo-change and dynamic-change exactness
2. raw part-name identity if that external contract matters
3. Rust migration only after preserving this exact falsifier matrix
