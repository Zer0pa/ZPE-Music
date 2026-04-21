from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests.common import FIXTURES, configure_env

configure_env()

from zpe_music.core.imc import IMCEncoder


def test_add_music_propagates_parser_dependency_failure(monkeypatch) -> None:
    def _raise_import_error(source: str) -> None:
        raise ImportError("music21 missing")

    monkeypatch.setattr("zpe_music.core.imc.musicxml_to_events", _raise_import_error)

    try:
        IMCEncoder().add_music(FIXTURES / "simple_scale.musicxml")
    except ImportError as exc:
        assert "music21 missing" in str(exc)
    else:  # pragma: no cover - defensive branch
        raise AssertionError("authoritative music parser failure should not fall back silently")
