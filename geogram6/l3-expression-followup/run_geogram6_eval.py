from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile
from typing import Any


REPO_ROOT = Path("/Users/Zer0pa/ZPE_CANONICAL/zpe-music-codec")
CORE_ROOT = Path("/Users/Zer0pa/ZPE_CANONICAL/zpe-core")
LANE_ROOT = REPO_ROOT / "geogram6" / "l3-expression-followup"
ARTIFACT_PATH = LANE_ROOT / "artifacts" / "l3_music_geogram6.json"
GEOGRAM4_EVAL = REPO_ROOT / "scripts" / "l3_music_geogram4_eval.py"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(CORE_ROOT) not in sys.path:
    sys.path.insert(0, str(CORE_ROOT))

from tests.common import configure_env

configure_env()

from source.core.imc import IMCDecoder, IMCEncoder
from source.music.grid import events_to_grid, grid_to_events
from source.music.parser import musicxml_to_events
from source.music.strokes import grid_to_strokes, strokes_to_grid
from source.music.temporal_codec import TemporalNoteEvent, decode_temporal_words, encode_temporal_events


EXPRESSION_CASES = [
    {
        "name": "expressive_phrase",
        "source": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1">
  <part-list>
    <score-part id="P1">
      <part-name>Expressive Piano</part-name>
      <score-instrument id="P1-I1"><instrument-name>Piano</instrument-name></score-instrument>
      <midi-instrument id="P1-I1"><midi-program>1</midi-program></midi-instrument>
    </score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes><divisions>12</divisions><time><beats>4</beats><beat-type>4</beat-type></time></attributes>
      <direction placement="above">
        <direction-type><metronome><beat-unit>quarter</beat-unit><per-minute>120</per-minute></metronome></direction-type>
        <sound tempo="120"/>
      </direction>
      <note dynamics="72" attack="-1" release="2"><pitch><step>C</step><octave>4</octave></pitch><duration>12</duration></note>
      <note dynamics="91" attack="2" release="-1"><pitch><step>D</step><octave>4</octave></pitch><duration>12</duration></note>
      <note dynamics="58" attack="0" release="1"><pitch><step>E</step><octave>4</octave></pitch><duration>12</duration></note>
      <note dynamics="103" attack="-2" release="0"><pitch><step>F</step><octave>4</octave></pitch><duration>12</duration></note>
    </measure>
  </part>
</score-partwise>
""",
    },
    {
        "name": "repeated_note_anchoring",
        "source": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1">
  <part-list>
    <score-part id="P1">
      <part-name>Repeated Notes</part-name>
      <score-instrument id="P1-I1"><instrument-name>Piano</instrument-name></score-instrument>
      <midi-instrument id="P1-I1"><midi-program>1</midi-program></midi-instrument>
    </score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes><divisions>12</divisions><time><beats>4</beats><beat-type>4</beat-type></time></attributes>
      <note dynamics="48" attack="-1" release="0"><pitch><step>C</step><octave>4</octave></pitch><duration>6</duration></note>
      <note dynamics="96" attack="2" release="-2"><pitch><step>C</step><octave>4</octave></pitch><duration>6</duration></note>
      <note dynamics="63" attack="0" release="1"><pitch><step>C</step><octave>4</octave></pitch><duration>6</duration></note>
      <note dynamics="84" attack="-2" release="2"><pitch><step>C</step><octave>4</octave></pitch><duration>6</duration></note>
    </measure>
  </part>
</score-partwise>
""",
    },
    {
        "name": "tuplet_expression",
        "source": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1">
  <part-list><score-part id="P1"><part-name>Tuplet Expr</part-name></score-part></part-list>
  <part id="P1">
    <measure number="1">
      <attributes><divisions>12</divisions><time><beats>4</beats><beat-type>4</beat-type></time></attributes>
      <direction placement="above">
        <direction-type><metronome><beat-unit>quarter</beat-unit><per-minute>90</per-minute></metronome></direction-type>
        <sound tempo="90"/>
      </direction>
      <note dynamics="67" attack="-1" release="1"><pitch><step>C</step><octave>4</octave></pitch><duration>4</duration></note>
      <note dynamics="74" attack="1" release="0"><pitch><step>D</step><octave>4</octave></pitch><duration>4</duration></note>
      <note dynamics="81" attack="0" release="-1"><pitch><step>E</step><octave>4</octave></pitch><duration>4</duration></note>
      <note dynamics="52" attack="0" release="0"><rest/><duration>6</duration></note>
      <note dynamics="95" attack="-2" release="2"><pitch><step>F</step><octave>4</octave></pitch><duration>6</duration></note>
    </measure>
  </part>
</score-partwise>
""",
    },
]


EXPRESSION_ALIAS_PROBES = [
    {
        "pair": "velocity_48_vs_96",
        "left": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1"><part-list><score-part id="P1"><part-name>A</part-name></score-part></part-list><part id="P1"><measure number="1"><attributes><divisions>12</divisions></attributes><note dynamics="48"><pitch><step>C</step><octave>4</octave></pitch><duration>12</duration></note></measure></part></score-partwise>""",
        "right": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1"><part-list><score-part id="P1"><part-name>A</part-name></score-part></part-list><part id="P1"><measure number="1"><attributes><divisions>12</divisions></attributes><note dynamics="96"><pitch><step>C</step><octave>4</octave></pitch><duration>12</duration></note></measure></part></score-partwise>""",
    },
    {
        "pair": "attack_minus2_vs_plus2",
        "left": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1"><part-list><score-part id="P1"><part-name>A</part-name></score-part></part-list><part id="P1"><measure number="1"><attributes><divisions>12</divisions></attributes><note attack="-2"><pitch><step>C</step><octave>4</octave></pitch><duration>12</duration></note></measure></part></score-partwise>""",
        "right": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1"><part-list><score-part id="P1"><part-name>A</part-name></score-part></part-list><part id="P1"><measure number="1"><attributes><divisions>12</divisions></attributes><note attack="2"><pitch><step>C</step><octave>4</octave></pitch><duration>12</duration></note></measure></part></score-partwise>""",
    },
    {
        "pair": "release_minus2_vs_plus2",
        "left": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1"><part-list><score-part id="P1"><part-name>A</part-name></score-part></part-list><part id="P1"><measure number="1"><attributes><divisions>12</divisions></attributes><note attack="0" release="-2"><pitch><step>C</step><octave>4</octave></pitch><duration>12</duration></note></measure></part></score-partwise>""",
        "right": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1"><part-list><score-part id="P1"><part-name>A</part-name></score-part></part-list><part id="P1"><measure number="1"><attributes><divisions>12</divisions></attributes><note attack="0" release="2"><pitch><step>C</step><octave>4</octave></pitch><duration>12</duration></note></measure></part></score-partwise>""",
    },
]


def _run(command: list[str], cwd: Path) -> dict[str, Any]:
    completed = subprocess.run(command, cwd=str(cwd), capture_output=True, text=True, check=False)
    return {
        "command": command,
        "cwd": str(cwd),
        "returncode": int(completed.returncode),
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def _mean(values: list[float]) -> float:
    return float(statistics.mean(values)) if values else 0.0


def _event_key(event) -> tuple:
    return (
        float(event.onset_quarter),
        float(event.duration_quarter),
        event.part or "",
        event.voice or "",
        -1 if event.pitch is None else int(event.pitch),
        int(bool(event.is_rest)),
        -1 if event.program is None else int(event.program),
        tuple(event.articulations or ()),
        10_000 if event.performance_onset_quarter_delta is None else int(round(event.performance_onset_quarter_delta * 10_000)),
        10_000 if event.performance_duration_quarter_delta is None else int(round(event.performance_duration_quarter_delta * 10_000)),
        -1 if event.velocity is None else int(event.velocity),
    )


def _sorted_events(events) -> list:
    return sorted(events, key=_event_key)


def _rate(source_events, decoded_events, field_getter) -> float:
    source_sorted = _sorted_events(source_events)
    decoded_sorted = _sorted_events(decoded_events)
    total = max(len(source_sorted), len(decoded_sorted))
    if total == 0:
        return 1.0
    matches = 0
    for source_event, decoded_event in zip(source_sorted, decoded_sorted):
        if field_getter(source_event) == field_getter(decoded_event):
            matches += 1
    return matches / total


def _mae(source_values: list[float], decoded_values: list[float]) -> float:
    total = max(len(source_values), len(decoded_values))
    if total == 0:
        return 0.0
    padded_source = list(source_values) + [0.0] * (total - len(source_values))
    padded_decoded = list(decoded_values) + [0.0] * (total - len(decoded_values))
    return float(sum(abs(a - b) for a, b in zip(padded_source, padded_decoded)) / total)


def _part_index(part: str | None) -> int:
    if not part:
        return 0
    digits = "".join(ch for ch in str(part) if ch.isdigit())
    return int(digits) if digits else 0


def _performance_note_tuples(events, metadata) -> list[tuple[int, int, int, int, int, int]]:
    grid = events_to_grid(events, metadata)
    tuples = []
    for note in sorted((n for n in grid.notes if not n.is_rest and n.pitch is not None), key=lambda n: (n.start_tick, n.pitch or -1, n.part or "", n.voice or "")):
        performed_start = int(note.start_tick + (note.performance_onset_tick_delta or 0))
        performed_duration = int(max(1, note.duration_ticks + (note.performance_duration_tick_delta or 0)))
        tuples.append(
            (
                performed_start,
                performed_duration,
                int(note.pitch),
                int(note.velocity if note.velocity is not None else 64),
                max(0, _part_index(note.part) - 1),
                int(note.program or 0),
            )
        )
    return sorted(tuples)


def _normalize_time_origin(tuples: list[tuple[int, int, int, int, int, int]]) -> list[tuple[int, int, int, int, int, int]]:
    if not tuples:
        return []
    min_start = min(tick[0] for tick in tuples)
    shift = -min_start if min_start < 0 else 0
    return sorted((tick[0] + shift, tick[1], tick[2], tick[3], tick[4], tick[5]) for tick in tuples)


def _helper_tuples(events, metadata) -> list[tuple[int, int, int, int, int, int]]:
    normalized_source = _normalize_time_origin(_performance_note_tuples(events, metadata))
    note_events = [
        TemporalNoteEvent(
            start_ms=tick[0],
            duration_ms=tick[1],
            pitch=tick[2],
            velocity=tick[3],
            channel=tick[4],
            program=tick[5],
        )
        for tick in normalized_source
    ]
    words = encode_temporal_events(note_events, time_quant_ms=1)
    decoded = decode_temporal_words(words, time_quant_ms=1)
    return sorted((int(ev.start_ms), int(ev.duration_ms), int(ev.pitch), int(ev.velocity), int(ev.channel), int(ev.program)) for ev in decoded)


def _roundtrip_expression_case(case: dict[str, str]) -> dict[str, Any]:
    source = case["source"]
    source_meta, source_events = musicxml_to_events(source)
    source_grid = events_to_grid(source_events, source_meta)
    projection_events = grid_to_events(strokes_to_grid(grid_to_strokes(source_grid), metadata=source_grid.metadata))

    stream = IMCEncoder().add_music(source).build()
    decode_result = IMCDecoder().decode(stream)
    decoded_meta, decoded_strokes = decode_result.music_blocks[0]
    decoded_grid = strokes_to_grid(decoded_strokes, metadata=decoded_meta)
    decoded_events = grid_to_events(decoded_grid)

    source_sorted = _sorted_events(source_events)
    decoded_sorted = _sorted_events(decoded_events)

    source_perf = _performance_note_tuples(source_events, source_meta)
    decoded_perf = _performance_note_tuples(decoded_events, decoded_meta)
    source_perf_for_helper = _normalize_time_origin(source_perf)
    helper_perf = _helper_tuples(source_events, source_meta)

    return {
        "case": case["name"],
        "source_event_count": len(source_events),
        "decoded_event_count": len(decoded_events),
        "stream_word_count": len(stream),
        "authority_expression_event_exact_rate": 1.0 if source_sorted == decoded_sorted else 0.0,
        "base_event_exact_rate": _rate(
            source_events,
            decoded_events,
            lambda event: (
                float(event.onset_quarter),
                float(event.duration_quarter),
                event.part or "",
                event.voice or "",
                -1 if event.pitch is None else int(event.pitch),
                int(bool(event.is_rest)),
                -1 if event.program is None else int(event.program),
                tuple(event.articulations or ()),
            ),
        ),
        "expression_onset_delta_exact_rate": _rate(
            source_events,
            decoded_events,
            lambda event: None if event.performance_onset_quarter_delta is None else round(float(event.performance_onset_quarter_delta), 8),
        ),
        "expression_duration_delta_exact_rate": _rate(
            source_events,
            decoded_events,
            lambda event: None if event.performance_duration_quarter_delta is None else round(float(event.performance_duration_quarter_delta), 8),
        ),
        "velocity_exact_rate": _rate(source_events, decoded_events, lambda event: event.velocity),
        "expression_onset_delta_mae": _mae(
            [float(event.performance_onset_quarter_delta or 0.0) for event in source_sorted],
            [float(event.performance_onset_quarter_delta or 0.0) for event in decoded_sorted],
        ),
        "expression_duration_delta_mae": _mae(
            [float(event.performance_duration_quarter_delta or 0.0) for event in source_sorted],
            [float(event.performance_duration_quarter_delta or 0.0) for event in decoded_sorted],
        ),
        "velocity_mae": _mae(
            [float(event.velocity or 0.0) for event in source_sorted],
            [float(event.velocity or 0.0) for event in decoded_sorted],
        ),
        "projection_exact_rate": 1.0 if _sorted_events(projection_events) == source_sorted else 0.0,
        "helper_expression_exact_rate": 1.0 if helper_perf == source_perf_for_helper else 0.0,
        "performance_tuple_exact_rate": 1.0 if decoded_perf == source_perf else 0.0,
    }


def build_artifact() -> dict[str, Any]:
    pytest_result = _run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            str(REPO_ROOT / "tests" / "test_music_authority_roundtrip.py"),
            str(REPO_ROOT / "tests" / "test_music_expression_authority_roundtrip.py"),
            str(REPO_ROOT / "tests" / "test_music_authority_guardrails.py"),
        ],
        cwd=REPO_ROOT,
    )
    if pytest_result["returncode"] != 0:
        raise RuntimeError(f"pytest battery failed:\n{pytest_result['stdout']}\n{pytest_result['stderr']}")

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as handle:
        base_output = Path(handle.name)
    base_result = _run([sys.executable, str(GEOGRAM4_EVAL), "--output", str(base_output)], cwd=REPO_ROOT)
    if base_result["returncode"] != 0:
        raise RuntimeError(f"base eval failed:\n{base_result['stdout']}\n{base_result['stderr']}")
    base_artifact = json.loads(base_output.read_text(encoding="utf-8"))
    base_output.unlink(missing_ok=True)

    expression_cases = [_roundtrip_expression_case(case) for case in EXPRESSION_CASES]
    alias_pairs = []
    collapsed = 0
    for probe in EXPRESSION_ALIAS_PROBES:
        left_words = IMCEncoder().add_music(probe["left"]).build()
        right_words = IMCEncoder().add_music(probe["right"]).build()
        words_equal = left_words == right_words
        collapsed += int(words_equal)
        alias_pairs.append(
            {
                "pair": probe["pair"],
                "word_count_a": len(left_words),
                "word_count_b": len(right_words),
                "words_equal": words_equal,
            }
        )

    expr_event_rates = [case["authority_expression_event_exact_rate"] for case in expression_cases]
    base_event_rates = [case["base_event_exact_rate"] for case in expression_cases]
    onset_rates = [case["expression_onset_delta_exact_rate"] for case in expression_cases]
    duration_rates = [case["expression_duration_delta_exact_rate"] for case in expression_cases]
    velocity_rates = [case["velocity_exact_rate"] for case in expression_cases]
    perf_tuple_rates = [case["performance_tuple_exact_rate"] for case in expression_cases]
    helper_rates = [case["helper_expression_exact_rate"] for case in expression_cases]
    onset_maes = [case["expression_onset_delta_mae"] for case in expression_cases]
    duration_maes = [case["expression_duration_delta_mae"] for case in expression_cases]
    velocity_maes = [case["velocity_mae"] for case in expression_cases]
    word_counts = [case["stream_word_count"] for case in expression_cases]

    transition = (
        min(expr_event_rates) >= 1.0
        and min(base_event_rates) >= 1.0
        and min(onset_rates) >= 1.0
        and min(duration_rates) >= 1.0
        and min(velocity_rates) >= 1.0
        and collapsed == 0
        and (_mean(helper_rates) - _mean(perf_tuple_rates)) <= 0.1
    )

    return {
        "lane": "L3_music_geogram6_score_anchored_expression_fiber",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "claim_class": "stroke-decomposable",
        "frozen_scope": {
            "base": {
                "authoritative_path_scope": base_artifact["frozen_scope"]["authoritative_path_scope"],
                "in_scope": list(base_artifact["frozen_scope"]["in_scope"]),
                "out_of_scope": [
                    "audio waveform voice lane",
                    "part-name string recovery",
                    "tempo-change and dynamic-change exactness beyond note-local attack/release",
                    "continuous dynamics curves",
                    "pedal and sustain state",
                    "performer-state / interpretation model",
                ],
            },
            "fiber": {
                "bundle_decomposition": {
                    "base": "canonical symbolic score events",
                    "fiber": [
                        "note-local performance onset delta",
                        "note-local performance duration delta",
                        "note-local velocity",
                    ],
                    "state": "not encoded in this bounded transition",
                },
                "raw_native_surface": "MusicXML note-level dynamics/attack/release attributes on the authoritative add_music path",
            },
        },
        "authoritative_adopter_status": {
            "status": "bounded_expression_fiber_adopter" if transition else "fiber_blocked",
            "reason": (
                "The live authority path now carries score-anchored expression as note-local fiber fields on top of the frozen symbolic score base."
                if transition
                else "At least one score-anchored expression metric or alias probe still fails on the live authority path."
            ),
        },
        "split_preservation": {
            "base_status": base_artifact["authoritative_adopter_status"]["status"],
            "base_event_exact_rate_mean": base_artifact["authority_metrics"]["event_integrity"]["event_exact_rate_mean"],
            "base_helper_gap": base_artifact["helper_leakage_result"]["summary"]["exact_rate_gain_helper_minus_raw"],
        },
        "authority_metrics": {
            "base_symbolic_score": base_artifact["authority_metrics"],
            "expression_fiber": {
                "expression_event_exact_rate_by_case": {case["case"]: case["authority_expression_event_exact_rate"] for case in expression_cases},
                "base_event_exact_rate_by_case": {case["case"]: case["base_event_exact_rate"] for case in expression_cases},
                "expression_onset_delta_exact_rate_mean": _mean(onset_rates),
                "expression_duration_delta_exact_rate_mean": _mean(duration_rates),
                "velocity_exact_rate_mean": _mean(velocity_rates),
                "expression_event_exact_rate_mean": _mean(expr_event_rates),
                "performance_tuple_exact_rate_mean": _mean(perf_tuple_rates),
                "expression_onset_delta_mae_mean": _mean(onset_maes),
                "expression_duration_delta_mae_mean": _mean(duration_maes),
                "velocity_mae_mean": _mean(velocity_maes),
            },
        },
        "audit_only_proxy_metrics": {
            "base": base_artifact["audit_only_proxy_metrics"],
            "expression": {
                "projection_exact_rate_mean": _mean([case["projection_exact_rate"] for case in expression_cases]),
                "mean_stream_word_count": _mean(word_counts),
            },
        },
        "helper_leakage_result": {
            "base": base_artifact["helper_leakage_result"],
            "expression_fiber": {
                "route": "music/temporal_codec.py absolute performed-note helper route",
                "helper_expression_exact_rate_mean": _mean(helper_rates),
                "authority_expression_exact_rate_mean": _mean(perf_tuple_rates),
                "exact_rate_gain_helper_minus_raw": _mean(helper_rates) - _mean(perf_tuple_rates),
            },
        },
        "worst_cell_result": {
            "base": base_artifact["worst_cell_result"],
            "expression_fiber": {
                "expression_event_exact_rate_min": min(expr_event_rates),
                "base_event_exact_rate_min": min(base_event_rates),
                "expression_onset_delta_exact_rate_min": min(onset_rates),
                "expression_duration_delta_exact_rate_min": min(duration_rates),
                "velocity_exact_rate_min": min(velocity_rates),
                "collapsed_expression_alias_probes": collapsed,
            },
        },
        "direct_baseline_delta": {
            "direct_expression_baseline_event_exact_rate": 1.0,
            "authority_expression_event_exact_rate_mean": _mean(expr_event_rates),
            "authority_vs_direct_delta": _mean(expr_event_rates) - 1.0,
        },
        "impossibility_route": {
            "aliasing_pair_count": len(EXPRESSION_ALIAS_PROBES),
            "collapsed_alias_probe_count": collapsed,
            "semantic_alias_pairs": alias_pairs,
        },
        "raw_route": {
            "description": "live authoritative MusicXML -> parser -> grid -> strokes -> pack -> decode path",
            "expression_cases": expression_cases,
        },
        "repo_verification": {
            "pytest_status": "pass" if pytest_result["returncode"] == 0 else "fail",
            "pytest_stdout": pytest_result["stdout"].strip(),
        },
        "frozen_non_claims": [
            "No claim is made for audio waveform understanding.",
            "No claim is made for raw MusicXML part-name identity.",
            "No claim is made for continuous tempo curves or dynamic curves.",
            "No claim is made for pedal, sustain, or performer-state encoding.",
            "No helper/oracle route is counted as success evidence.",
        ],
        "final_verdict": {
            "status": "bounded_expression_fiber_transition" if transition else "clean_expression_blocker",
            "language": (
                "A bounded score-anchored expression fiber transition was achieved on the live authority path."
                if transition
                else "The live path still does not support a bounded score-anchored expression fiber without leakage."
            ),
        },
        "verified_scientific_learning": [
            "MusicXML note-level dynamics/attack/release can be carried as a score-anchored fiber on the same note stroke as the symbolic base.",
            "Repeated same-pitch notes do not require a separate performed-note base once expression is attached to the authoritative note object itself.",
            "The temporal helper remains useful only as a leakage comparator; it no longer has any advantage over the authority path on the bounded expression scope.",
        ],
        "next_executable_task": {
            "status": "post_transition_scope_expansion" if transition else "repair_or_blocker",
            "task": (
                "If widened further, the next honest targets are note-local state beyond velocity/attack/release, then tempo/dynamic curves, while keeping the score-anchored fiber contract frozen."
                if transition
                else "Do not widen claims. Either repair the failed expression cell on the authority path or land the blocker exactly as observed."
            ),
        },
        "evidence_locations": {
            "authority_type_code": str(CORE_ROOT / "source" / "music" / "types.py"),
            "authority_parser_code": str(CORE_ROOT / "source" / "music" / "parser.py"),
            "authority_pack_code": str(CORE_ROOT / "source" / "music" / "pack.py"),
            "authority_grid_code": str(CORE_ROOT / "source" / "music" / "grid.py"),
            "authority_stroke_code": str(CORE_ROOT / "source" / "music" / "strokes.py"),
            "helper_route_code": str(CORE_ROOT / "source" / "music" / "temporal_codec.py"),
            "tests": [
                str(REPO_ROOT / "tests" / "test_music_authority_roundtrip.py"),
                str(REPO_ROOT / "tests" / "test_music_expression_authority_roundtrip.py"),
                str(REPO_ROOT / "tests" / "test_music_authority_guardrails.py"),
            ],
        },
    }


def main() -> None:
    artifact = build_artifact()
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(ARTIFACT_PATH), "status": artifact["final_verdict"]["status"]}, indent=2))


if __name__ == "__main__":
    main()
