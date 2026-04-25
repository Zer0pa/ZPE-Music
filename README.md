# zpe-music

[![License: SAL v7.0](https://img.shields.io/badge/license-SAL%20v7.0-e5e7eb?labelColor=111111)](LICENSE)

**6/6 exact roundtrip metrics. 11/11 checks passing. Bounded symbolic-score codec with note-local expression refinement. No audio waveforms. No comp benchmarks.**

`zpe-music` is part of the [Zer0pa](https://github.com/Zer0pa) portfolio of encoding products — one of 17 independent domain codecs, each with its own proof surface.

## What This Is

`zpe-music` is a music encoding product for canonical symbolic score data, with a bounded note-local expression refinement carried on the same score note. It targets MusicXML pipelines that need auditable roundtrip recovery of score structure plus note-local `attack`, `release`, and `dynamics`-derived fields.

It does not do audio understanding. The public surface is canonical symbolic score plus a bounded note-local expression refinement, and the hard boundaries are stated explicitly below.

## Key Metrics

| Metric | Value | Proof artifact | CI test |
|--------|-------|----------------|---------|
| SCORE_EVENT_EXACT (`score_event_exact_rate_mean`) | 1.0 | `proofs/artifacts/music_release_metrics.json` | `tests/test_music_authority_roundtrip.py` |
| PART_EXACT (`part_exact_rate_mean`) | 1.0 | `proofs/artifacts/music_release_metrics.json` | `tests/test_music_authority_roundtrip.py` |
| ARTICULATION_EXACT (`articulation_exact_rate_mean`) | 1.0 | `proofs/artifacts/music_release_metrics.json` | `tests/test_music_authority_roundtrip.py` |
| EXPRESSION_EVENT_EXACT (`expression_event_exact_rate_mean`) | 1.0 | `proofs/artifacts/music_release_metrics.json` | `tests/test_music_expression_authority_roundtrip.py` |
| PERFORMANCE_TUPLE_EXACT (`performance_tuple_exact_rate_mean`) | 1.0 | `proofs/artifacts/music_release_metrics.json` | `tests/test_music_expression_authority_roundtrip.py` |
| REPEATED_NOTE_CASE (`repeated_note_case_exact_rate`) | 1.0 | `proofs/artifacts/music_release_metrics.json` | `tests/test_music_expression_authority_roundtrip.py::test_repeated_note_expression_roundtrip_exact` |
| REQUIRED_CHECKS_PASSED | 11/11 in 3.39 s | `validation/results/release_verification.json` | `validation/run_release_verification.py` |

All seven metrics measured on the bounded authority test corpus (11 synthetic/controlled MusicXML cases). These are test-corpus results on the authority path, not production-generality claims. This is a symbolic-score codec — no audio codec comp benchmarks (MP3/AAC/Opus/MIDI/MusicGen) exist or apply.

Source: `proofs/artifacts/music_release_metrics.json`, `validation/results/release_verification.json`

## Commercial Readiness

| Field | Value |
|-------|-------|
| Verdict | STAGED |
| Scope | Bounded authority path on synthetic/controlled MusicXML corpus |
| Comp benchmarks | NOT CLAIMED — symbolic-score codec; no audio codec baseline applies |
| Production generality | Not claimed beyond authority corpus |
| Always-in-beta | Useful now on the bounded path; improving continuously |

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
