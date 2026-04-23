# ZPE-Music Novelty Card

**Product:** ZPE-Music
**Domain:** Deterministic symbolic-score encoding with bounded note-local expression carried on the same authority-native score note.
**What we sell:** Exact round-trip serialization of canonical symbolic score structure with bounded note-local expression attachment for auditable MusicXML pipelines.

## Novel contributions

1. **Score-note base with note-local expression fiber** — The product keeps the authority-native score note as the base object and carries bounded expression on that same note rather than emitting a second performed-note stream. `src/zpe_music/music/parser.py` extracts score notes together with note-local `attack`, `release`, and `dynamics` fields, and `src/zpe_music/music/pack.py` emits those fields as typed control words bound to the same note event. The novel contribution is the score-note-plus-expression-fiber contract itself.

2. **Deterministic same-pitch repeated-note disambiguation** — Repeated same-pitch notes retain distinct expression attachment instead of collapsing onto a pitch-only key. The repeated-note merge and active-note tracking live in `src/zpe_music/music/parser.py`, and `tests/test_music_expression_authority_roundtrip.py` includes the repeated-note authority cases that prove per-note expression identity survives. The novel contribution is the deterministic attachment surface for repeated same-pitch score notes.

## Standard techniques used (explicit, not novel)

- MusicXML parsing and canonical symbolic-score extraction
- Fixed-width control-word packing for bounded metadata and expression fields
- Delta encoding for onset and duration refinement
- Deterministic label registries for part and voice identifiers
- pytest-based regression verification

## Compass-8 / 8-primitive architecture

NO. LICENSE §7.10 is authoritative.

This product's novelty surface is symbolic-score structure plus bounded note-local expression. The repository contains directional-token helper code under `src/zpe_music/diagram/`, but that is not the product claim surface and is not a Novel Contribution of ZPE-Music.

## Open novelty questions for the license agent

- None in this pass.
