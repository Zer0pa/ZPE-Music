# Scope

## Public Product Boundary

`zpe-music` publicly claims a bounded codec for canonical symbolic score plus a bounded note-local expression refinement.

### In Scope

- MusicXML score-note parsing on the authority path
- canonical symbolic score events
- onset and duration in quarter-note units
- pitch or rest identity
- canonical part identity
- canonical voice identity
- per-event program
- supported articulation flags
- note-local `attack`, `release`, and `dynamics`-derived refinement carried on the same score note

### Out Of Scope

- waveform or audio understanding
- continuous tempo curves
- continuous dynamics curves
- pedal or sustain state
- performer-state or interpretation models
- raw MusicXML part-name identity

## Hard Boundary

The earned expression surface is bounded to note-local refinement only. A separate performed-note stream is outside the public boundary.
