# Reproducibility

## Canonical Inputs

- `fixtures/simple_scale.musicxml`: canonical MusicXML fixture used by the
  fresh-clone verification path

The repeated-note authority cases in the public test battery are constructed in
`tests/test_music_expression_authority_roundtrip.py`; no separate repeated-note
fixture file is committed in this repo.

## Golden-Bundle Hash

This field will be populated by the `receipt-bundle.yml` workflow in Wave 3.

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

- CPython 3.10+ via `src/zpe_music/`

No alternate runtime surface is claimed in this repo.
