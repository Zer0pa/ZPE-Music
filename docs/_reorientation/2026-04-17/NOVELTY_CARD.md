# ZPE-Music Novelty Card

**Product:** ZPE-Music
**Domain:** Canonical symbolic score encoding — MusicXML note events, part/voice identity, rest and articulation preservation, and bounded note-local expression fields (attack, release, dynamics-derived)
**What we sell:** Auditable, lossless roundtrip of canonical symbolic score structure plus bounded per-note expression refinements, suitable for MusicXML pipelines that need verifiable recovery of score identity without audio or performance modeling

## Novel contributions

1. **Bounded note-local expression refinement on the score anchor** — The codec carries `attack`, `release`, and `dynamics`-derived fields on the same score-anchored note object rather than as a separate performance layer. This keeps expressive data co-located with the note it modifies while maintaining strict scope — no continuous curves, no pedal state, no performer modeling. Code: [`src/zpe_music/music/types.py`](../../src/zpe_music/music/types.py) (MusicStroke dataclass, `performance_onset_tick_delta`, `performance_duration_tick_delta`, `velocity` fields). Nearest prior art: MIDI, MusicXML `<note>` with `<dynamics>`. What is genuinely new: the explicit bounding of expression to the note anchor within a codec that also preserves canonical score identity — the codec commits to the minimal expression surface and proves roundtrip accuracy on that surface.

2. **Repeated same-pitch note distinguishability** — The grid representation maintains unique note identity across consecutive same-pitch notes, which is a known failure mode in symbolic score roundtrip codecs. This is proven as a hard cell in the test battery. Code: [`src/zpe_music/music/grid.py`](../../src/zpe_music/music/grid.py) (note ordering logic) and [`tests/test_music_authority_roundtrip.py`](../../tests/test_music_authority_roundtrip.py) (REPEATED_NOTE_CASE).

3. **Explicit part/voice/program preservation in the stroke layer** — Each stroke carries part index, voice index, and per-event program as first-class fields, not derived post-hoc. This allows authority-path roundtrip of multi-instrument, multi-voice scores. Code: [`src/zpe_music/music/strokes.py:11-30`](../../src/zpe_music/music/strokes.py) (MusicStroke construction in `grid_to_strokes`).

## Standard techniques used (explicit, not novel)

- Score grid representation (time-tick × pitch grid): standard approach in piano-roll and symbolic score systems
- Variable-length integer packing (run-length encoding of note durations): standard
- Bitfield subtype layout in packed word format (`SUBTYPE_BOUNDARY`, `SUBTYPE_MOVE_T`, etc.): standard binary codec practice
- Delta encoding for performance timing fields: standard
- MusicXML as source/sink format: standard

## Compass-8 / 8-primitive architecture

NO — ZPE-Music does not implement the Compass-8 pattern. The codec shares the `DrawDir` / `DIRS` data structure from `src/zpe_music/diagram/quantize.py` (which defines 8 cardinal/diagonal directions), but `strokes.py` uses only `DrawDir(0)` — direction 0, rightward — to encode note duration as a time-forward horizontal run. No diagonal or vertical direction codes are used in the music encoding path. The 8-direction vocabulary is imported but not exercised beyond direction 0. The LICENSE §7.10 correctly declares `Compass-8 Pattern: NO`.

Code citation: [`src/zpe_music/music/strokes.py:17`](../../src/zpe_music/music/strokes.py) — `commands.append(DrawDir(0))` — the sole direction used.

## Open novelty questions for the license agent

- None. The scope is cleanly bounded: canonical score + note-local expression. No unresolved novelty ambiguity.
