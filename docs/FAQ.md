# FAQ

## Does this repo understand audio?

No. The public surface is symbolic score plus a bounded note-local expression refinement.

## What expression data is actually supported?

Only note-local refinement derived from MusicXML `attack`, `release`, and `dynamics` on the same score note.

## Does this repo claim pedal, sustain, or continuous expressive curves?

No.

## Why is the runtime vendored locally?

Because each ZPE repo is an independent product repo, not a module of a shared public platform.
