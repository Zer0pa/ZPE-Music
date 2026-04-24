# Reproducibility

## Canonical Inputs

- `fixtures/simple_scale.musicxml` - bounded symbolic-score plus note-local expression fixture used by the public authority and guardrail batteries

## Golden-Bundle Hash

The canonical golden-bundle hash will be populated by the `receipt-bundle.yml` workflow in Wave 3. Until then, the governing public proof anchors are:

- `proofs/artifacts/music_release_metrics.json`
- `validation/results/release_verification.json`

## Verification Command

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
python validation/run_release_verification.py
python -m pytest -q tests/test_music_authority_roundtrip.py tests/test_music_expression_authority_roundtrip.py tests/test_music_authority_guardrails.py
```

## Supported Runtimes

- Python 3.10+ on the standalone `zpe-music` repository surface
- MusicXML score input through the vendored `music21`-backed parser path
- No Rust, WASM, Swift, C#, waveform, or performer-state runtime is shipped by this repo
