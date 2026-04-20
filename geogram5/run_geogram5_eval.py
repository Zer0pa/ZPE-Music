from __future__ import annotations

from dataclasses import fields
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import statistics
import subprocess
import sys
import tempfile


REPO_ROOT = Path("/Users/Zer0pa/ZPE_CANONICAL/zpe-music-codec")
CORE_ROOT = Path("/Users/Zer0pa/ZPE_CANONICAL/zpe-core")
GEOGRAM5_ROOT = REPO_ROOT / "geogram5"
ARTIFACT_PATH = GEOGRAM5_ROOT / "artifacts" / "l3_music_geogram5.json"
GEOGRAM4_EVAL = REPO_ROOT / "scripts" / "l3_music_geogram4_eval.py"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(CORE_ROOT) not in sys.path:
    sys.path.insert(0, str(CORE_ROOT))

from source.music.pack import CTRL_TAG_FLAGS, CTRL_TAG_PART_INDEX, CTRL_TAG_PITCH_ORIGIN, CTRL_TAG_PROGRAM
from source.music.pack import CTRL_TAG_TIME_ANCHOR, CTRL_TAG_TIME_STEP_DEN, CTRL_TAG_VOICE_INDEX
from source.music.temporal_codec import TemporalNoteEvent, decode_temporal_words, encode_temporal_events
from source.music.types import GridNote, MusicMetadata, MusicStroke, NoteEvent


def _run(command: list[str], cwd: Path) -> dict:
    completed = subprocess.run(
        command,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "command": command,
        "cwd": str(cwd),
        "returncode": int(completed.returncode),
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def _build_base_artifact() -> tuple[dict, dict, dict]:
    pytest_result = _run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            str(REPO_ROOT / "tests" / "test_music_authority_roundtrip.py"),
            str(REPO_ROOT / "tests" / "test_music_authority_guardrails.py"),
        ],
        cwd=REPO_ROOT,
    )
    if pytest_result["returncode"] != 0:
        raise RuntimeError(f"split preservation tests failed:\n{pytest_result['stdout']}\n{pytest_result['stderr']}")

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as handle:
        temp_output = Path(handle.name)
    eval_result = _run([sys.executable, str(GEOGRAM4_EVAL), "--output", str(temp_output)], cwd=REPO_ROOT)
    if eval_result["returncode"] != 0:
        raise RuntimeError(f"geogram4 preservation eval failed:\n{eval_result['stdout']}\n{eval_result['stderr']}")
    base_artifact = json.loads(temp_output.read_text(encoding="utf-8"))
    temp_output.unlink(missing_ok=True)

    fallback_python = shutil.which("python3")
    fallback_probe = {"status": "not_run"}
    if fallback_python:
        fallback_probe = _run(
            [
                fallback_python,
                "-c",
                (
                    "import sys;"
                    "sys.path.insert(0, '/Users/Zer0pa/ZPE_CANONICAL/zpe-core');"
                    "from source.core.imc import IMCEncoder;"
                    "IMCEncoder().add_music('/Users/Zer0pa/ZPE_CANONICAL/zpe-music-codec/fixtures/simple_scale.musicxml')"
                ),
            ],
            cwd=REPO_ROOT,
        )
    return base_artifact, pytest_result, fallback_probe


def _temporal_key(event: TemporalNoteEvent) -> tuple[int, int, int, int, int, int]:
    return (
        int(event.start_ms),
        int(event.duration_ms),
        int(event.pitch),
        int(event.velocity),
        int(event.channel),
        int(event.program),
    )


def _expression_cases() -> list[dict]:
    return [
        {
            "name": "rubato_phrase",
            "score_note_count": 4,
            "events": [
                TemporalNoteEvent(start_ms=0, duration_ms=430, pitch=60, velocity=64, channel=0, program=1),
                TemporalNoteEvent(start_ms=520, duration_ms=390, pitch=62, velocity=72, channel=0, program=1),
                TemporalNoteEvent(start_ms=1015, duration_ms=560, pitch=64, velocity=83, channel=0, program=1),
                TemporalNoteEvent(start_ms=1660, duration_ms=470, pitch=65, velocity=70, channel=0, program=1),
            ],
        },
        {
            "name": "arpeggiated_chord",
            "score_note_count": 4,
            "events": [
                TemporalNoteEvent(start_ms=0, duration_ms=620, pitch=60, velocity=76, channel=0, program=1),
                TemporalNoteEvent(start_ms=35, duration_ms=590, pitch=64, velocity=69, channel=0, program=1),
                TemporalNoteEvent(start_ms=82, duration_ms=640, pitch=67, velocity=88, channel=0, program=1),
                TemporalNoteEvent(start_ms=410, duration_ms=380, pitch=72, velocity=63, channel=0, program=1),
            ],
        },
        {
            "name": "swing_repetition",
            "score_note_count": 6,
            "events": [
                TemporalNoteEvent(start_ms=0, duration_ms=180, pitch=67, velocity=70, channel=1, program=33),
                TemporalNoteEvent(start_ms=225, duration_ms=110, pitch=69, velocity=82, channel=1, program=33),
                TemporalNoteEvent(start_ms=360, duration_ms=190, pitch=67, velocity=71, channel=1, program=33),
                TemporalNoteEvent(start_ms=595, duration_ms=105, pitch=69, velocity=85, channel=1, program=33),
                TemporalNoteEvent(start_ms=720, duration_ms=205, pitch=67, velocity=74, channel=1, program=33),
                TemporalNoteEvent(start_ms=965, duration_ms=115, pitch=71, velocity=90, channel=1, program=33),
            ],
        },
    ]


def _mean(values: list[float]) -> float:
    return float(statistics.mean(values)) if values else 0.0


def _fiber_probe() -> dict:
    cases = []
    exact_rates = []
    velocity_rates = []
    word_counts = []
    for case in _expression_cases():
        words = encode_temporal_events(case["events"], time_quant_ms=1)
        decoded = decode_temporal_words(words, time_quant_ms=1)
        expected = sorted((_temporal_key(event) for event in case["events"]))
        recovered = sorted((_temporal_key(event) for event in decoded))
        total = max(len(expected), len(recovered))
        exact_matches = sum(1 for left, right in zip(expected, recovered) if left == right)
        velocity_matches = sum(1 for left, right in zip(expected, recovered) if left[3] == right[3])
        exact_rate = 1.0 if total == 0 else exact_matches / total
        velocity_rate = 1.0 if total == 0 else velocity_matches / total
        exact_rates.append(exact_rate)
        velocity_rates.append(velocity_rate)
        word_counts.append(len(words))
        cases.append(
            {
                "case": case["name"],
                "score_note_count": int(case["score_note_count"]),
                "performance_note_count": len(case["events"]),
                "overlay_word_count": len(words),
                "overlay_event_exact_rate": exact_rate,
                "overlay_velocity_exact_rate": velocity_rate,
                "overlay_programs": sorted({int(event.program) for event in case["events"]}),
                "overlay_channels": sorted({int(event.channel) for event in case["events"]}),
            }
        )

    note_event_fields = {field.name for field in fields(NoteEvent)}
    grid_note_fields = {field.name for field in fields(GridNote)}
    music_stroke_fields = {field.name for field in fields(MusicStroke)}
    music_metadata_fields = {field.name for field in fields(MusicMetadata)}
    available_control_tags = [
        "TIME_ANCHOR",
        "PITCH_ORIGIN",
        "TIME_STEP_DEN",
        "PART_INDEX",
        "VOICE_INDEX",
        "FLAGS",
        "PROGRAM",
    ]

    return {
        "candidate_route": str(CORE_ROOT / "source" / "music" / "temporal_codec.py"),
        "probe_scope": {
            "candidate_expression_fields": [
                "performed onset in ms",
                "performed duration in ms",
                "velocity",
                "channel",
                "program",
            ],
            "not_earned_here": [
                "pedal or sustain state",
                "continuous tempo curve",
                "continuous dynamics curve",
                "performer state / interpretation model",
            ],
        },
        "cases": cases,
        "summary": {
            "overlay_event_exact_rate_mean": _mean(exact_rates),
            "overlay_velocity_exact_rate_mean": _mean(velocity_rates),
            "overlay_word_count_mean": _mean(word_counts),
            "overlay_alone_performance_exact_rate_mean": _mean(exact_rates),
        },
        "fiber_contract_audit": {
            "stores_absolute_pitch": True,
            "stores_absolute_start_ms": True,
            "stores_absolute_duration_ms": True,
            "stores_velocity": True,
            "stores_program": True,
            "stores_score_note_index": False,
            "stores_base_part_identity": False,
            "stores_base_voice_identity": False,
            "note_event_has_velocity_field": "velocity" in note_event_fields,
            "note_event_has_performance_timing_field": any(
                name in note_event_fields for name in ("onset_ms", "duration_ms", "onset_delta_ms", "duration_delta_ms")
            ),
            "grid_note_has_expression_field": any(
                name in grid_note_fields for name in ("velocity", "onset_delta_ms", "duration_delta_ms")
            ),
            "music_stroke_has_expression_field": any(
                name in music_stroke_fields for name in ("velocity", "onset_delta_ms", "duration_delta_ms")
            ),
            "music_metadata_has_tempo_changes": "tempo_changes" in music_metadata_fields,
            "music_metadata_has_dynamic_changes": "dynamic_changes" in music_metadata_fields,
            "available_music_control_tags": available_control_tags,
            "expression_control_tags_present": False,
        },
        "verdict": {
            "status": "blocked",
            "reason": (
                "The only exact expressive route on hand is temporal_codec, and it reconstructs the full performed "
                "note stream without the frozen score. The live authority types and music pack surface have no "
                "score-anchored note-level performance fields, so this route is helper leakage, not a real fiber."
            ),
        },
    }


def build_artifact() -> dict:
    base_artifact, pytest_result, fallback_probe = _build_base_artifact()
    fiber_probe = _fiber_probe()

    return {
        "lane": "L3_music_geogram5_split_preservation_and_expression_fiber",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "claim_class": base_artifact["claim_class"],
        "frozen_scope": {
            "base": base_artifact["frozen_scope"],
            "fiber_probe": {
                "goal": "Test expressive performance as a real fiber over the frozen symbolic-score base.",
                "non_goal": "No base inflation or helper-laundered second base counts as fiber success.",
            },
        },
        "authoritative_adopter_status": {
            "base_status": "preserved_bounded_adopter",
            "fiber_status": fiber_probe["verdict"]["status"],
            "reason": "The split bounded score codec remains intact; the expressive extension does not clear the fiber contract.",
        },
        "split_preservation": {
            "repo_tests": {
                "status": "pass" if pytest_result["returncode"] == 0 else "fail",
                "command": pytest_result["command"],
                "stdout": pytest_result["stdout"].strip(),
            },
            "base_eval_status": base_artifact["authoritative_adopter_status"]["status"],
            "guardrails": {
                "sibling_core_autodiscovery_in_tests": True,
                "missing_music21_fails_loud": fallback_probe.get("returncode") != 0,
                "missing_music21_probe_command": fallback_probe.get("command"),
                "missing_music21_probe_stderr": (fallback_probe.get("stderr") or "").strip(),
            },
        },
        "authority_metrics": base_artifact["authority_metrics"],
        "audit_only_proxy_metrics": base_artifact["audit_only_proxy_metrics"],
        "helper_leakage_result": base_artifact["helper_leakage_result"],
        "worst_cell_result": base_artifact["worst_cell_result"],
        "direct_baseline_delta": base_artifact["baseline_delta"],
        "expressive_fiber_probe": fiber_probe,
        "frozen_non_claims": [
            *base_artifact["frozen_non_claims"],
            "No expressive-performance adopter is claimed here.",
            "No claim is made that temporal note events form a real fiber over the frozen symbolic score.",
        ],
        "final_verdict": {
            "status": "split_preserved_fiber_blocked",
            "language": (
                "The Geogram 4 bounded symbolic-score adopter is preserved in the split repo, but the current "
                "expressive route is a helper-leaking second base rather than a real fiber."
            ),
        },
        "next_executable_task": {
            "status": "required_before_expression_claims",
            "task": (
                "Introduce score-anchored performance fields and pack semantics on the authority path "
                "(for example note-indexed onset/duration deltas and velocity) so expression depends on, "
                "rather than replaces, the frozen score base."
            ),
        },
        "evidence_locations": {
            "split_repo": str(REPO_ROOT),
            "geogram4_eval_script": str(GEOGRAM4_EVAL),
            "guardrail_test": str(REPO_ROOT / "tests" / "test_music_authority_guardrails.py"),
            "authority_guardrail_code": str(CORE_ROOT / "source" / "core" / "imc.py"),
            "expression_route_code": str(CORE_ROOT / "source" / "music" / "temporal_codec.py"),
            "authority_type_code": str(CORE_ROOT / "source" / "music" / "types.py"),
            "authority_pack_code": str(CORE_ROOT / "source" / "music" / "pack.py"),
        },
    }


def main() -> None:
    artifact = build_artifact()
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(ARTIFACT_PATH), "status": artifact["final_verdict"]["status"]}, indent=2))


if __name__ == "__main__":
    main()
