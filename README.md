# zpe-music

[![License: SAL v7.0](https://img.shields.io/badge/license-SAL%20v7.0-e5e7eb?labelColor=111111)](LICENSE)

**6/6 exact roundtrip metrics. 11/11 checks passing. Bounded symbolic-score codec with note-local expression refinement. No audio waveforms. No comp benchmarks.**

`zpe-music` is part of the [Zer0pa](https://github.com/Zer0pa) portfolio of encoding products — one of 17 independent domain codecs, each with its own proof surface.

## What This Is

Canonical symbolic-score codec. MusicXML score structure plus note-local attack, release, and dynamics-derived fields round-trip under the declared proof surface.

It does not do audio understanding. The public surface is canonical symbolic score plus a bounded note-local expression refinement, and the hard boundaries are stated explicitly below.

## Codec Mechanics

<p>
  <img src=".github/assets/readme/lane-mechanics/MUSIC.gif" alt="ZPE-Music Codec Mechanics animation" width="100%">
</p>

| Field | Value |
| ------- | ------- |
| Architecture | MUSIC_STREAM |
| Encoding | MUSIC_SYMBOLIC_V1 |
| Mechanics Asset | `.github/assets/readme/lane-mechanics/MUSIC.gif` |

## Key Metrics

| Metric | Value | Baseline |
| -------- | ------- | ---------- |
| SCORE_EVENT_EXACT (score_event_exact_rate_mean) | 1.0 | — |
| PART_EXACT (part_exact_rate_mean) | 1.0 | — |
| ARTICULATION_EXACT (articulation_exact_rate_mean) | 1.0 | — |
| EXPRESSION_EVENT_EXACT (expression_event_exact_rate_mean) | 1.0 | — |

> Source: `proofs/artifacts/music_release_metrics.json`, `validation/results/release_verification.json`

## Repo Identity

| Field | Value |
| ------- | ------- |
| Identifier | ZPE-Music |
| Repository | https://github.com/Zer0pa/ZPE-Music |
| Section | encoding |
| Visibility | PUBLIC |
| Architecture | MUSIC_STREAM |
| Encoding | MUSIC_SYMBOLIC_V1 |
| Commit SHA | cdd6b75 |
| License | SAL-7.0 |
| Authority Source | proofs/artifacts/music_release_metrics.json |

## Readiness

| Field | Value |
| ------- | ------- |
| Verdict | STAGED |
| Checks | 7/7 |
| Anchors | 2 display anchors |
| Commit | cdd6b75 |
| Authority | proofs/artifacts/music_release_metrics.json |

### Honest Blocker

Audio waveform understanding or performer-audio interpretation.; Continuous tempo curves or continuous dynamics curves.; Pedal, sustain, performer state, or general expressive performance modeling.

## What We Prove

- Canonical symbolic score events roundtrip exactly on the verified authority path.
- Part, voice, rest, articulation, and per-event program survive the bounded score surface exactly.
- Note-local expression fields derived from MusicXML attack, release, and dynamics roundtrip exactly on the same score-anchored note object.
- Repeated same-pitch notes remain distinguishable on the bounded expression cases.

## What We Don't Claim

- Audio waveform understanding or performer-audio interpretation.
- Continuous tempo curves or continuous dynamics curves.
- Pedal, sustain, performer state, or general expressive performance modeling.
- Raw MusicXML part-name identity recovery.
- Anything beyond bounded note-local attack, release, and dynamics-derived refinement.
- MP3/AAC/Opus/MIDI/MusicGen baselines — this is a symbolic codec; no audio codec comparisons exist or apply.

## Verification Status

| Code | Check | Verdict |
| ------ | ------- | --------- |
| V_01 | Score event exact roundtrip — tests/test_music_authority_roundtrip.py | PASS |
| V_02 | Part, voice, rest, articulation, program exact roundtrip — tests/test_music_authority_roundtrip.py | PASS |
| V_03 | Expression event exact roundtrip — tests/test_music_expression_authority_roundtrip.py | PASS |
| V_04 | Performance tuple exact roundtrip — tests/test_music_expression_authority_roundtrip.py | PASS |
| V_05 | Repeated same-pitch note distinguishability — tests/test_music_expression_authority_roundtrip.py::test_repeated_note_expression_roundtrip_exact | PASS |
| V_06 | Guardrail battery (out-of-scope rejection) — tests/test_music_authority_guardrails.py | PASS |
| V_07 | Release verification suite 11/11 — validation/run_release_verification.py | PASS |

## Proof Anchors

| Path | State |
| ------ | ------- |
| `proofs/artifacts/music_release_metrics.json` | VERIFIED |
| `validation/results/release_verification.json` | VERIFIED |

## Repo Shape

| Field | Value |
| ------- | ------- |
| Proof Anchors | 2 display anchors |
| Modality Lanes | 1 |
| Architecture | MUSIC_STREAM |
| Encoding | MUSIC_SYMBOLIC_V1 |
| Verification | 7/7 checks |
| Authority Source | proofs/artifacts/music_release_metrics.json |

## Extended Metrics

Detailed metric rows retained from the previous `## Key Metrics` section. The public product page uses the four-row summary above.

Additional verified metrics (not in the 4-row canonical table, included for full disclosure):

| Metric | Value | Proof artifact | CI test |
|--------|-------|----------------|---------|
| PERFORMANCE_TUPLE_EXACT (`performance_tuple_exact_rate_mean`) | 1.0 | `proofs/artifacts/music_release_metrics.json` | `tests/test_music_expression_authority_roundtrip.py` |
| REPEATED_NOTE_CASE (`repeated_note_case_exact_rate`) | 1.0 | `proofs/artifacts/music_release_metrics.json` | `tests/test_music_expression_authority_roundtrip.py::test_repeated_note_expression_roundtrip_exact` |
| REQUIRED_CHECKS_PASSED | 11/11 in 3.39 s | `validation/results/release_verification.json` | `validation/run_release_verification.py` |

## Quick Start

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
python validation/run_release_verification.py
python -m pytest -q tests/test_music_authority_roundtrip.py tests/test_music_expression_authority_roundtrip.py tests/test_music_authority_guardrails.py
```

## Upcoming Workstreams

This section captures the active lane priorities — what the next agent or contributor picks up, and what investors should expect. Cadence is continuous, not milestoned.

- **Real MusicXML corpus benchmark** — Active Engineering. Benchmark against MuseScore open scores (~50) and IMSLP MusicXML exports (~50) to validate the authority path beyond the 11 synthetic cases.
