# Architecture

## Runtime Map

The public authority path is:

`IMCEncoder.add_music -> zpe_music/music/parser.py -> zpe_music/music/grid.py -> zpe_music/music/strokes.py -> zpe_music/music/pack.py -> IMCDecoder music block reconstruction`

## Repo-Local Runtime

This repo vendors the minimum runtime it needs inside `src/zpe_music/` so that `zpe-music` stands alone as an independent product repo.

- `src/zpe_music/core/imc.py`: music-only IMC encode/decode wrapper used by the public tests
- `src/zpe_music/music/`: authoritative music parser, grid, stroke, and pack runtime
- `src/zpe_music/diagram/quantize.py`: minimal geometry primitives used by the music stroke path

## Verified Surface

- canonical symbolic score events
- part and voice identity
- per-event program
- rest and articulation preservation
- note-local performance onset delta
- note-local performance duration delta
- note-local velocity

## Explicitly Not In Scope

- waveform understanding
- continuous curves
- pedal or sustain state
- performer-state modeling
