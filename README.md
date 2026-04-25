# zpe-music

[![License: SAL v7.0](https://img.shields.io/badge/license-SAL%20v7.0-e5e7eb?labelColor=111111)](LICENSE)

## What This Is

`zpe-music` is a music encoding product for canonical symbolic score data, with a bounded note-local expression refinement carried on the same score note. It targets MusicXML pipelines that need auditable roundtrip recovery of score structure plus note-local `attack`, `release`, and `dynamics`-derived fields.

It does not do audio understanding. The public surface is canonical symbolic score plus a bounded note-local expression refinement, and the hard boundaries are stated explicitly below.

## Key Metrics

| Metric | Value | Baseline |
|-------|-------|----------|
| SCORE_EVENT_EXACT | 1.0 | Direct |
| EXPRESSION_EVENT_EXACT | 1.0 | Direct |
| REPEATED_NOTE_CASE | 1.0 | Hard cell |
| REQUIRED_CHECKS | 11/11 | Battery |

> Source: `proofs/artifacts/music_release_metrics.json`, `validation/results/release_verification.json`

## What We Prove

- Canonical symbolic score events roundtrip exactly on the verified authority path.
- Part, voice, rest, articulation, and per-event program survive the bounded score surface exactly.
- Note-local expression fields derived from MusicXML `attack`, `release`, and `dynamics` roundtrip exactly on the same score-anchored note object.
- Repeated same-pitch notes remain distinguishable on the bounded expression cases.

## What We Don't Claim

- Audio waveform understanding or performer-audio interpretation.
- Continuous tempo curves or continuous dynamics curves.
- Pedal, sustain, performer state, or general expressive performance modeling.
- Raw MusicXML part-name identity recovery.
- Anything beyond bounded note-local `attack`, `release`, and `dynamics`-derived refinement.

## Verification Surface

- Proof metrics: `proofs/artifacts/music_release_metrics.json`
- Reproducible verification output: `validation/results/release_verification.json`
- Verification entrypoint: `validation/run_release_verification.py`
- Authority roundtrip battery: `tests/test_music_authority_roundtrip.py`
- Expression roundtrip battery: `tests/test_music_expression_authority_roundtrip.py`
- Guardrail battery: `tests/test_music_authority_guardrails.py`

## Quick Start

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
python validation/run_release_verification.py
python -m pytest -q tests/test_music_authority_roundtrip.py tests/test_music_expression_authority_roundtrip.py tests/test_music_authority_guardrails.py
```
