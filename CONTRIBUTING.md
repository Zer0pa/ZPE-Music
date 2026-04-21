# Contributing

Thanks for contributing to `zpe-music`.

## Ground Rules

- Keep claims inside the verified public scope.
- Do not widen the product boundary by implication.
- Keep waveform, continuous curves, pedal, sustain, and performer-state claims out of scope unless new proof anchors are added first.
- Use a named branch for changes.
- Run the public verification surface before opening a PR.

## Local Checks

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
python validation/run_release_verification.py
python -m pytest -q tests/test_music_authority_roundtrip.py tests/test_music_expression_authority_roundtrip.py tests/test_music_authority_guardrails.py
```

## Pull Requests

- Describe the bounded scope touched by the change.
- Link the proof anchor or validation result that supports the claim.
- Keep documentation honest about what the codec does not claim.
