from __future__ import annotations

import os
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = ROOT / "src"
FIXTURES = ROOT / "fixtures"


src_root_text = str(SRC_ROOT)
if src_root_text not in sys.path:
    sys.path.insert(0, src_root_text)


def configure_env() -> None:
    os.environ.setdefault("STROKEGRAM_ENABLE_DIAGRAM", "1")
    os.environ.setdefault("STROKEGRAM_ENABLE_MUSIC", "1")
    os.environ.setdefault("STROKEGRAM_ENABLE_VOICE", "1")
