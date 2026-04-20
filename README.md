# zpe-music-codec

Bounded symbolic-score codec split out of the IMC monorepo.

This repo owns the Geogram 4 `L3` bounded release surface:

- canonical symbolic score events
- part and voice identity
- per-event program
- rest and articulation preservation

Out of scope:

- waveform or voice understanding
- raw part-name identity
- expressive performance nuance

Install `zpe-core` first in the same environment, then install this repo and run the standalone test and matrix bundle.
