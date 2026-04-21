from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = REPO_ROOT / "validation" / "results" / "release_verification.json"
METRICS_PATH = REPO_ROOT / "proofs" / "artifacts" / "music_release_metrics.json"
TEST_FILES = [
    REPO_ROOT / "tests" / "test_music_authority_roundtrip.py",
    REPO_ROOT / "tests" / "test_music_expression_authority_roundtrip.py",
    REPO_ROOT / "tests" / "test_music_authority_guardrails.py",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=RESULT_PATH)
    args = parser.parse_args()

    command = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        *[str(path) for path in TEST_FILES],
    ]
    completed = subprocess.run(
        command,
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    result = {
        "product": "zpe-music",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "pass" if completed.returncode == 0 else "fail",
        "pytest": {
            "command": ["python", "-m", "pytest", "-q", *[str(path.relative_to(REPO_ROOT)) for path in TEST_FILES]],
            "returncode": int(completed.returncode),
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        },
        "governing_metrics": metrics["authority_metrics"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "status": result["status"]}))


if __name__ == "__main__":
    main()
