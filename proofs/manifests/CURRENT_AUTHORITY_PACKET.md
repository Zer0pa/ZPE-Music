# Current Authority Packet

## Product

`zpe-music`

## Public Claim

Bounded canonical symbolic-score codec with a bounded note-local expression refinement on the same authority path.

## Authority Path

`IMCEncoder.add_music -> zpe_music/music/parser.py -> zpe_music/music/grid.py -> zpe_music/music/strokes.py -> zpe_music/music/pack.py -> IMCDecoder music block reconstruction`

## Governing Proof Anchors

- `proofs/artifacts/music_release_metrics.json`
- `validation/results/release_verification.json`
- `tests/test_music_authority_roundtrip.py`
- `tests/test_music_expression_authority_roundtrip.py`
- `tests/test_music_authority_guardrails.py`

## Public Non-Claims

- no waveform understanding
- no continuous tempo or dynamics curves
- no pedal or sustain state
- no performer-state claim

## Reference Commit

`c99638f2691a`
