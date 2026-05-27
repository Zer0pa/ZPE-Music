# ZPE-Music

> Product-page mirror for `/encoding/ZPE-Music/`.
> Live public repo: [Zer0pa/ZPE-Music](https://github.com/Zer0pa/ZPE-Music).
> GitHub Markdown cannot reproduce the website typography, CSS, JavaScript, scroll behavior, or live bento layout; this README translates the product page into GitHub-safe Markdown evidence blocks.

## 0. Install / Developer Commands

The product page is the positioning authority. This section is the only retained developer-surface material from the previous root README.

```bash
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
python -m pytest -q tests/test_music_authority_roundtrip.py tests/test_music_expression_authority_roundtrip.py tests/test_music_authority_guardrails.py
```

## Product Page Mirror

**Product-page title:** ZPE-Music · MusicXML you can round-trip · Zer0pa

**Product-page description:** ZPE-Music · bounded symbolic-score codec · MusicXML round-trip across six exactness axes · 6/6 metrics at 1.0 under 11/11 release checks in 3.39s · synthetic authority surface · real-corpus benchmark active, not done · PyPI v0.1.0 stale pending release

### Hero Translation

> 00 · ZPE-MUSIC · SYMBOLIC SCORE CODECDEVELOPER-READY · REAL-CORPUS OPEN Encoding the music inside music The score codec — what the composer wrote, not what the orchestra played · ZPE-Music · PyPI zpe-music 0.1.0 · github.com/Zer0pa/ZPE-Music A recording captures what an orchestra sounded like on one Tuesday night. A score captures what the composer meant — every event, voice, articulation and expression beneath the sound. Every audio codec eats the score and emits a waveform. ZPE-Music does the opposite: it encodes the score itself. On the declared MusicXML score surface, all six exactness axes resolve at 1.0 under 11/11 release checks. Real-corpus work against MuseScore and IMSLP catalogues is active, not done.

## Positioning

| Field | Value |
| --- | --- |
| Section | encoding |
| Product route | /encoding/ZPE-Music/ |
| Live public repository | https://github.com/Zer0pa/ZPE-Music |
| Repo identity used here | ZPE-Music |
| Website display identity | ZPE-Music |
| Verdict | STAGED |
| Posture | always_in_beta |
| Headline metric | All four exact-roundtrip rates at 1.0 on the bounded authority test corpus (11 synthetic/controlled MusicXML cases). |
| Honest blocker | Audio waveform understanding or performer-audio interpretation.; Continuous tempo curves or continuous dynamics curves.; Pedal, sustain, performer state, or general expressive performance modeling. |
| Mechanics asset from product page | MUSIC.gif |

## Key Metrics

| Metric | Value | Baseline |
| --- | --- | --- |
| SCORE_EVENT_EXACT (score_event_exact_rate_mean) | 1.0 | — |
| PART_EXACT (part_exact_rate_mean) | 1.0 | — |
| ARTICULATION_EXACT (articulation_exact_rate_mean) | 1.0 | — |
| EXPRESSION_EVENT_EXACT (expression_event_exact_rate_mean) | 1.0 | — |

## Proof Anchors

| Path | State |
| --- | --- |
| proofs/artifacts/music_release_metrics.json | VERIFIED |
| validation/results/release_verification.json | VERIFIED |

## What We Prove

- Canonical symbolic score events roundtrip exactly on the verified authority path.
- Part, voice, rest, articulation, and per-event program survive the bounded score surface exactly.
- Note-local expression fields derived from MusicXML attack, release, and dynamics roundtrip exactly on the same score-anchored note object.
- Repeated same-pitch notes remain distinguishable on the bounded expression cases.

## What We Do Not Claim

- Audio waveform understanding or performer-audio interpretation.
- Continuous tempo curves or continuous dynamics curves.
- Pedal, sustain, performer state, or general expressive performance modeling.
- Raw MusicXML part-name identity recovery.
- Anything beyond bounded note-local attack, release, and dynamics-derived refinement.
- MP3/AAC/Opus/MIDI/MusicGen baselines — this is a symbolic codec; no audio codec comparisons exist or apply.

## Blockers / Failures

> Audio waveform understanding or performer-audio interpretation.; Continuous tempo curves or continuous dynamics curves.; Pedal, sustain, performer state, or general expressive performance modeling.

## Verification Surface

| Code | Check | Verdict |
| --- | --- | --- |
| V_01 | Score event exact roundtrip — tests/test_music_authority_roundtrip.py | PASS |
| V_02 | Part, voice, rest, articulation, program exact roundtrip — tests/test_music_authority_roundtrip.py | PASS |
| V_03 | Expression event exact roundtrip — tests/test_music_expression_authority_roundtrip.py | PASS |
| V_04 | Performance tuple exact roundtrip — tests/test_music_expression_authority_roundtrip.py | PASS |
| V_05 | Repeated same-pitch note distinguishability — tests/test_music_expression_authority_roundtrip.py::test_repeated_note_expression_roundtrip_exact | PASS |
| V_06 | Guardrail battery (out-of-scope rejection) — tests/test_music_authority_guardrails.py | PASS |
| V_07 | Release verification suite 11/11 — validation/run_release_verification.py | PASS |

## License

| Field | Value |
| --- | --- |
| License | SAL-7.0 |
| Authority source | proofs/artifacts/music_release_metrics.json |

## Upcoming Workstreams

| Category | Summary |
| --- | --- |
| Active Engineering | Real MusicXML corpus benchmark; benchmark against MuseScore open scores (~50) and IMSLP MusicXML exports (~50) to validate the authority path beyond the 11 synthetic cases. |

## Related Repos

No related repos are declared on the product page frontmatter.

<details>
<summary>Full Visible Product-Page Bento Translation</summary>

This section preserves the product page cells as Markdown text blocks. It intentionally omits shared site navigation, footer chrome, CSS, and scripts.

### Bento Cell 1

> 00 · ZPE-MUSIC · SYMBOLIC SCORE CODECDEVELOPER-READY · REAL-CORPUS OPEN Encoding the music inside music The score codec — what the composer wrote, not what the orchestra played · ZPE-Music · PyPI zpe-music 0.1.0 · github.com/Zer0pa/ZPE-Music A recording captures what an orchestra sounded like on one Tuesday night. A score captures what the composer meant — every event, voice, articulation and expression beneath the sound. Every audio codec eats the score and emits a waveform. ZPE-Music does the opposite: it encodes the score itself. On the declared MusicXML score surface, all six exactness axes resolve at 1.0 under 11/11 release checks. Real-corpus work against MuseScore and IMSLP catalogues is active, not done.

### Bento Cell 2

> 01 · THE GAPSCORE BECOMES SOUND When a score is encoded as a waveform, the composer's intention disappears — it can't come back.

### Bento Cell 3

> 02 · MARKETSADJACENT FORECASTS Music publishing'32 · $13.7B Music publishing'30 · $10.8B Digital sheet music'34 · $4.2B Music education softwareest. $3.4B Rights management / score archiveest. $1.2B Symbolic-score archives have no published analyst category — MusicXML volume sits inside music-publishing and rights-management forecasts.

### Bento Cell 4

> 03 · VALUE $10.8B Music publishing grows; the symbolic-score archive sits unpriced inside publisher and rights workflows.

### Bento Cell 5

> 04 · INSIGHT A waveform keeps the sound. A score keeps the music.

### Bento Cell 6

> 05.1 · CURRENT TECHCODECS EAT THE SCORE DAWs encode audio. Streaming platforms deliver waveforms. AI music systems learn from recordings. The written structure beneath the sound — events, voices, articulation, expression — is outside every test. Codecs eat it and emit sound.

### Bento Cell 7

> 05.2 · OUR TECHKEEP THE SCORE ZPE-Music encodes the score itself. On the declared MusicXML score surface it preserves events, parts, voices, articulations, expression fields, performance tuples and repeated-pitch notes, decoding byte-identical to the input. All six exactness axes resolve at 1.0 across 11/11 release checks in 3.39 s. Audio interpretation is explicitly out of scope.

### Bento Cell 8

> 05.3 · BENCHMARKSMUSICXML SCORE SURFACE Axes6 / 6exactness 1.0 Checks11 / 11release pass Verify3.39seconds PyPI0.1.0stale pending SCORE_EVENT1.000 5 other axes1.000 real-corpuspending Surface: bounded MusicXML · real-corpus benchmark against MuseScore + IMSLP still pending.

### Bento Cell 9

> 06 · MEASUREMENTRELEASE ARTIFACT PROOFS Six axes. Six exactness claims. Each checked against a release artifact.

### Bento Cell 10

> 06.1 · COMPARATIVE PERFORMANCEMUSICXML 4.0 SCORE SURFACE SCORE_EVENT1.000 PART1.000 ARTICULATION1.000 EXPRESSION · PERF_TUPLE · REPEATED_NOTE1.000 music_release_metrics.json + release_verification.json · 11 passed · 3.39 s · PyPI 0.1.0 stale. Six axes on the MusicXML 4.0 score surface. Audio, MIDI, continuous dynamics, pedal and performer state are out of scope. Source: github.com/Zer0pa/ZPE-Music.

### Bento Cell 11

> 07 · KEY METRICSMUSICXML RELEASE PROOFS

### Bento Cell 12

> 07.1 · SCORE AXES 6 / 6EXACT Every axis at exactness 1.000

### Bento Cell 13

> 07.2 · RELEASE CHECKS 11 / 11PASS pytest score suite · strict

### Bento Cell 14

> 07.3 · VERIFY RUNTIME 3.39s Release suite · 2026-04-25

### Bento Cell 15

> 07.4 · REAL-CORPUS null MuseScore + IMSLP · active, not done

### Bento Cell 16

> 07.5 · PUBLIC PYPI 0.1.0 Connected · stale pending release

### Bento Cell 17

> 08 · SCORE FIDELITYDECLARED FIELDS ONLY Encode the declared score. Decode the declared score. The intention survives.

### Bento Cell 18

> 08.1 · WHAT DETERMINISTIC MEANSPER-ROUNDTRIP, SCORE NOT SOUND Deterministic here means per-roundtrip, and it means the score, not the sound. On the declared MusicXML score surface, encode and decode reproduce the canonical fields across all six axes — SCORE_EVENT, PART, ARTICULATION, EXPRESSION, PERF_TUPLE, REPEATED_NOTE — resolving at exactly 1.0 in 3.39 seconds. Audio waveforms, MIDI rendering, continuous tempo, dynamics curves, pedal state and performer state are outside the verified scope. We do not yet make the byte-identical claim against public real-corpus MusicXML; the MuseScore and IMSLP benchmark is active, not done.

### Bento Cell 19

> 08.2 · HONEST BLOCKER Honest Blocker · Out of scope: audio waveforms, MIDI benchmarks, continuous tempo and dynamics curves, pedal and sustain state, performer state, raw MusicXML part-name identity. Next step: close the public MuseScore and IMSLP corpus benchmark, refresh the stale 0.1.0 PyPI release, and publish the corrected build with the real-corpus result attached.

### Bento Cell 20

> 09 WHAT THE COMPOSER ACTUALLY WROTE.

### Bento Cell 21

> 09.1 · THE AMBITION The aim is a score that travels as the score — every event, voice, articulation and expression intact — instead of being flattened into a waveform every time it moves. A music industry built on recordings finally gets a first-class symbolic carrier for the work beneath the sound.

### Bento Cell 22

> 09.2 · WHAT WORKS NOW On declared MusicXML today: six exactness axes at 1.0, eleven of eleven release checks pass in 3.39 s.

### Bento Cell 23

> 09.3 · WHAT'S STILL OPEN The public MuseScore and IMSLP corpus benchmark is active, and the 0.1.0 PyPI release is stale pending refresh.

### Bento Cell 24

> 09.4 · INTERCHANGE · NEAR-TERM (12–24 MO) Scores move between editors without loss A composer hands a Finale file to an engraver who opens it in Dorico, the engraver returns it through a publisher in Sibelius, and every voice, articulation and tied note arrives in the same place it started — no rebuild pass.

### Bento Cell 25

> 09.5 · ARCHIVES · NEAR-TERM (12–24 MO) Catalogue librarians get a fidelity receipt A music library that holds a publisher's MusicXML catalogue can prove the Beethoven sonata in the 2024 archive is exactly the score on the 2026 reading stand. The proof is a packet comparison, not a side-by-side render.

### Bento Cell 26

> 09.6 · VERSIONING · MID-TERM (24–48 MO) Commissioned works carry a revision history A composer revising a string quartet for a chamber orchestra and the publisher tracking changes both see exactly which bars moved between draft three and draft four. Score editing becomes a tracked process, the way code review is, instead of a stack of PDFs.

### Bento Cell 27

> 09.7 · MUSIC AI · MID-TERM (24–48 MO) Symbolic music models train on clean ground truth A music-AI team building a transformer over symbolic scores stops fighting the inconsistencies of heterogeneous MusicXML exports. The training corpus arrives in one encoded form, and the model learns the music a composer wrote rather than the quirks of the editor that exported it.

### Bento Cell 28

> 09.8 · IDENTITY · PARADIGM (48 MO+) A musical work gets a fingerprint Two encodings of the same Bach prelude — one from a 19th-century scholarly edition, one from a modern engraver — produce comparable packets. Rights societies, publishers and academic catalogues can talk about the work itself, not the file format that happened to carry it.

</details>

---

Source mapping: product route `/encoding/ZPE-Music/` -> live public repo `Zer0pa/ZPE-Music`. README generated from product-page authority plus retained install/dev commands only.
