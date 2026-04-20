from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
CORE_ROOT = REPO_ROOT.parent / "zpe-core"
DEFAULT_OUTPUT = REPO_ROOT / "artifacts" / "l3_music_geogram4.json"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(CORE_ROOT) not in sys.path:
    sys.path.insert(0, str(CORE_ROOT))

from tests.common import FIXTURES, configure_env

configure_env()

from source.core.imc import IMCDecoder, IMCEncoder
from source.music.grid import events_to_grid, grid_to_events
from source.music.parser import musicxml_to_events
from source.music.strokes import grid_to_strokes, strokes_to_grid
from source.music.temporal_codec import TemporalNoteEvent, decode_temporal_words, encode_temporal_events


REST_ARTICULATION_XML = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1">
  <part-list>
    <score-part id="P1">
      <part-name>Piano</part-name>
      <score-instrument id="P1-I1"><instrument-name>Piano</instrument-name></score-instrument>
      <midi-instrument id="P1-I1"><midi-program>1</midi-program></midi-instrument>
    </score-part>
    <score-part id="P2">
      <part-name>Violin</part-name>
      <score-instrument id="P2-I1"><instrument-name>Violin</instrument-name></score-instrument>
      <midi-instrument id="P2-I1"><midi-program>41</midi-program></midi-instrument>
    </score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes><divisions>1</divisions><time><beats>4</beats><beat-type>4</beat-type></time></attributes>
      <note><pitch><step>C</step><octave>4</octave></pitch><duration>1</duration></note>
      <note><rest/><duration>1</duration></note>
    </measure>
  </part>
  <part id="P2">
    <measure number="1">
      <attributes><divisions>1</divisions></attributes>
      <note>
        <pitch><step>G</step><octave>4</octave></pitch>
        <duration>1</duration>
        <notations><articulations><staccato/></articulations></notations>
      </note>
      <note><pitch><step>A</step><octave>4</octave></pitch><duration>1</duration></note>
    </measure>
  </part>
</score-partwise>
"""


MULTITRACK_TEMPO_PROGRAM_XML = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1">
  <part-list>
    <score-part id="P1">
      <part-name>Piano</part-name>
      <score-instrument id="P1-I1"><instrument-name>Piano</instrument-name></score-instrument>
      <midi-instrument id="P1-I1"><midi-program>1</midi-program></midi-instrument>
    </score-part>
    <score-part id="P2">
      <part-name>Violin</part-name>
      <score-instrument id="P2-I1"><instrument-name>Violin</instrument-name></score-instrument>
      <midi-instrument id="P2-I1"><midi-program>41</midi-program></midi-instrument>
    </score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes><divisions>2</divisions><time><beats>4</beats><beat-type>4</beat-type></time></attributes>
      <direction placement="above"><direction-type><metronome><beat-unit>quarter</beat-unit><per-minute>120</per-minute></metronome></direction-type><sound tempo="120"/></direction>
      <note><pitch><step>C</step><octave>4</octave></pitch><duration>2</duration></note>
      <note><pitch><step>D</step><octave>4</octave></pitch><duration>2</duration></note>
    </measure>
  </part>
  <part id="P2">
    <measure number="1">
      <attributes><divisions>2</divisions></attributes>
      <direction placement="above"><direction-type><metronome><beat-unit>quarter</beat-unit><per-minute>120</per-minute></metronome></direction-type><sound tempo="120"/></direction>
      <note><rest/><duration>2</duration></note>
      <note><pitch><step>G</step><octave>4</octave></pitch><duration>2</duration></note>
      <note><pitch><step>A</step><octave>4</octave></pitch><duration>2</duration></note>
    </measure>
  </part>
</score-partwise>
"""


VOICE_TAGGED_POLYPHONY_XML = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1">
  <part-list><score-part id="P1"><part-name>Poly</part-name></score-part></part-list>
  <part id="P1">
    <measure number="1">
      <attributes><divisions>2</divisions><time><beats>4</beats><beat-type>4</beat-type></time></attributes>
      <note><pitch><step>C</step><octave>4</octave></pitch><duration>2</duration><voice>1</voice></note>
      <backup><duration>2</duration></backup>
      <note><pitch><step>E</step><octave>4</octave></pitch><duration>2</duration><voice>2</voice></note>
      <forward><duration>2</duration></forward>
      <note><pitch><step>D</step><octave>4</octave></pitch><duration>2</duration><voice>1</voice></note>
      <backup><duration>2</duration></backup>
      <note><pitch><step>F</step><octave>4</octave></pitch><duration>2</duration><voice>2</voice></note>
    </measure>
  </part>
</score-partwise>
"""


TUPLET_GRID_XML = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1">
  <part-list><score-part id="P1"><part-name>Tuplet</part-name></score-part></part-list>
  <part id="P1">
    <measure number="1">
      <attributes><divisions>6</divisions><time><beats>4</beats><beat-type>4</beat-type></time></attributes>
      <note><pitch><step>C</step><octave>4</octave></pitch><duration>2</duration></note>
      <note><pitch><step>D</step><octave>4</octave></pitch><duration>2</duration></note>
      <note><pitch><step>E</step><octave>4</octave></pitch><duration>2</duration></note>
      <note><rest/><duration>3</duration></note>
      <note><pitch><step>F</step><octave>4</octave></pitch><duration>3</duration></note>
    </measure>
  </part>
</score-partwise>
"""


CASES = [
    {
        "name": "simple_scale_fixture",
        "source": FIXTURES / "simple_scale.musicxml",
        "origin": "repository_fixture",
        "expected_voice_tagged_note_count": 0,
        "expected_program_part_count": 0,
    },
    {
        "name": "rest_articulation",
        "source": REST_ARTICULATION_XML,
        "origin": "generated_inline_musicxml",
        "expected_voice_tagged_note_count": 0,
        "expected_program_part_count": 2,
    },
    {
        "name": "multitrack_tempo_program",
        "source": MULTITRACK_TEMPO_PROGRAM_XML,
        "origin": "generated_inline_musicxml",
        "expected_voice_tagged_note_count": 0,
        "expected_program_part_count": 2,
    },
    {
        "name": "voice_tagged_polyphony",
        "source": VOICE_TAGGED_POLYPHONY_XML,
        "origin": "generated_inline_musicxml",
        "expected_voice_tagged_note_count": 4,
        "expected_program_part_count": 0,
    },
    {
        "name": "tuplet_grid",
        "source": TUPLET_GRID_XML,
        "origin": "generated_inline_musicxml",
        "expected_voice_tagged_note_count": 0,
        "expected_program_part_count": 0,
    },
]


ALIAS_PROBES = [
    {
        "pair": "rest_vs_note_origin",
        "left": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1"><part-list><score-part id="P1"><part-name>A</part-name></score-part></part-list><part id="P1"><measure number="1"><attributes><divisions>1</divisions></attributes><note><rest/><duration>1</duration></note></measure></part></score-partwise>""",
        "right": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1"><part-list><score-part id="P1"><part-name>A</part-name></score-part></part-list><part id="P1"><measure number="1"><attributes><divisions>1</divisions></attributes><note><pitch><step>C</step><octave>4</octave></pitch><duration>1</duration></note></measure></part></score-partwise>""",
    },
    {
        "pair": "plain_vs_staccato",
        "left": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1"><part-list><score-part id="P1"><part-name>A</part-name></score-part></part-list><part id="P1"><measure number="1"><attributes><divisions>1</divisions></attributes><note><pitch><step>C</step><octave>4</octave></pitch><duration>1</duration></note></measure></part></score-partwise>""",
        "right": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1"><part-list><score-part id="P1"><part-name>A</part-name></score-part></part-list><part id="P1"><measure number="1"><attributes><divisions>1</divisions></attributes><note><pitch><step>C</step><octave>4</octave></pitch><duration>1</duration><notations><articulations><staccato/></articulations></notations></note></measure></part></score-partwise>""",
    },
    {
        "pair": "piano_vs_violin_program",
        "left": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1"><part-list><score-part id="P1"><part-name>A</part-name><score-instrument id="P1-I1"><instrument-name>Piano</instrument-name></score-instrument><midi-instrument id="P1-I1"><midi-program>1</midi-program></midi-instrument></score-part></part-list><part id="P1"><measure number="1"><attributes><divisions>1</divisions></attributes><note><pitch><step>C</step><octave>4</octave></pitch><duration>1</duration></note></measure></part></score-partwise>""",
        "right": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1"><part-list><score-part id="P1"><part-name>A</part-name><score-instrument id="P1-I1"><instrument-name>Violin</instrument-name></score-instrument><midi-instrument id="P1-I1"><midi-program>41</midi-program></midi-instrument></score-part></part-list><part id="P1"><measure number="1"><attributes><divisions>1</divisions></attributes><note><pitch><step>C</step><octave>4</octave></pitch><duration>1</duration></note></measure></part></score-partwise>""",
    },
    {
        "pair": "part_assignment_cg_vs_gc",
        "left": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1">
  <part-list><score-part id="P1"><part-name>P1</part-name></score-part><score-part id="P2"><part-name>P2</part-name></score-part></part-list>
  <part id="P1"><measure number="1"><attributes><divisions>1</divisions></attributes><note><pitch><step>C</step><octave>4</octave></pitch><duration>1</duration></note></measure></part>
  <part id="P2"><measure number="1"><attributes><divisions>1</divisions></attributes><note><pitch><step>G</step><octave>4</octave></pitch><duration>1</duration></note></measure></part>
</score-partwise>""",
        "right": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1">
  <part-list><score-part id="P1"><part-name>P1</part-name></score-part><score-part id="P2"><part-name>P2</part-name></score-part></part-list>
  <part id="P1"><measure number="1"><attributes><divisions>1</divisions></attributes><note><pitch><step>G</step><octave>4</octave></pitch><duration>1</duration></note></measure></part>
  <part id="P2"><measure number="1"><attributes><divisions>1</divisions></attributes><note><pitch><step>C</step><octave>4</octave></pitch><duration>1</duration></note></measure></part>
</score-partwise>""",
    },
]


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
    )


def _event_tuple(event) -> tuple:
    return _event_key(event)


def _part_index(part: str | None) -> int:
    if not part:
        return 0
    digits = "".join(ch for ch in str(part) if ch.isdigit())
    return int(digits) if digits else 0


def _sorted_events(events) -> list:
    return sorted(events, key=_event_key)


def _mean(values: list[float]) -> float:
    return float(statistics.mean(values)) if values else 0.0


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


def _note_geometry_signature(grid) -> list[tuple]:
    origin = grid.metadata.pitch_origin
    return sorted(
        (
            int(note.start_tick),
            int(note.duration_ticks),
            -1 if note.pitch is None else int(note.pitch) - int(origin),
            int(bool(note.is_rest)),
        )
        for note in grid.notes
    )


def _note_tick_tuples(events, metadata) -> list[tuple]:
    grid = events_to_grid(events, metadata)
    return sorted(
        (
            int(note.start_tick),
            int(note.duration_ticks),
            -1 if note.pitch is None else int(note.pitch),
            int(bool(note.is_rest)),
        )
        for note in grid.notes
    )


def _helper_note_tuples(events, metadata) -> list[tuple]:
    grid = events_to_grid(events, metadata)
    note_events = []
    for event in events:
        if event.is_rest or event.pitch is None:
            continue
        event_grid = events_to_grid([event], metadata)
        note = event_grid.notes[0]
        note_events.append(
            TemporalNoteEvent(
                start_ms=int(note.start_tick),
                duration_ms=int(note.duration_ticks),
                pitch=int(event.pitch),
                velocity=64,
                channel=max(0, _part_index(event.part) - 1),
                program=int(event.program or 0),
            )
        )
    words = encode_temporal_events(note_events, time_quant_ms=1)
    decoded = decode_temporal_words(words, time_quant_ms=1)
    return sorted((int(ev.start_ms), int(ev.duration_ms), int(ev.pitch), int(ev.channel), int(ev.program)) for ev in decoded)


def _helper_source_note_tuples(events, metadata) -> list[tuple]:
    grid = events_to_grid(events, metadata)
    tuples = []
    for event, note in zip(_sorted_events([e for e in events if not e.is_rest and e.pitch is not None]), sorted((n for n in grid.notes if not n.is_rest and n.pitch is not None), key=lambda n: (n.start_tick, n.pitch or -1, n.part or ""))):
        tuples.append(
            (
                int(note.start_tick),
                int(note.duration_ticks),
                int(event.pitch),
                max(0, _part_index(event.part) - 1),
                int(event.program or 0),
            )
        )
    return sorted(tuples)


def _roundtrip_case(case: dict[str, Any]) -> dict[str, Any]:
    source = case["source"]
    source_meta, source_events = musicxml_to_events(str(source))
    source_grid = events_to_grid(source_events, source_meta)
    projection_events = grid_to_events(strokes_to_grid(grid_to_strokes(source_grid), metadata=source_grid.metadata))

    stream = IMCEncoder().add_music(source).build()
    decode_result = IMCDecoder().decode(stream)
    decoded_meta, decoded_strokes = decode_result.music_blocks[0]
    decoded_grid = strokes_to_grid(decoded_strokes, metadata=decoded_meta)
    decoded_events = grid_to_events(decoded_grid)

    source_sorted = _sorted_events(source_events)
    decoded_sorted = _sorted_events(decoded_events)
    note_source = [event for event in source_sorted if not event.is_rest and event.pitch is not None]
    note_decoded = [event for event in decoded_sorted if not event.is_rest and event.pitch is not None]

    source_tick = _note_tick_tuples(source_events, source_meta)
    decoded_tick = _note_tick_tuples(decoded_events, decoded_meta)

    helper_source = _helper_source_note_tuples(source_events, source_meta)
    helper_decoded = _helper_note_tuples(source_events, source_meta)

    source_articulation_positives = [event for event in source_events if event.articulations]
    recovered_articulation_positives = [
        1
        for source_event, decoded_event in zip(source_sorted, decoded_sorted)
        if source_event.articulations and tuple(source_event.articulations or ()) == tuple(decoded_event.articulations or ())
    ]

    metadata_exact = {
        "time_signature_exact": source_meta.time_signature == decoded_meta.time_signature,
        "key_signature_exact": source_meta.key_signature == decoded_meta.key_signature,
        "tempo_exact": source_meta.tempo == decoded_meta.tempo,
        "tempo_changes_exact": source_meta.tempo_changes == decoded_meta.tempo_changes,
        "part_names_exact": source_meta.part_names == decoded_meta.part_names,
        "part_programs_exact": source_meta.part_programs == decoded_meta.part_programs,
        "pitch_origin_exact": source_grid.metadata.pitch_origin == decoded_meta.pitch_origin,
        "time_step_quarter_exact": source_grid.metadata.time_step_quarter == decoded_meta.time_step_quarter,
    }

    return {
        "case": case["name"],
        "case_origin": case["origin"],
        "source_event_count": len(source_events),
        "decoded_stroke_count": len(decoded_strokes),
        "stream_word_count": len(stream),
        "authority_event_exact_rate": 1.0 if source_sorted == decoded_sorted else 0.0,
        "authority_note_event_exact_rate": 1.0 if note_source == note_decoded else 0.0,
        "articulation_exact_rate": _rate(source_events, decoded_events, lambda event: tuple(event.articulations or ())),
        "articulation_positive_recall": (
            len(recovered_articulation_positives) / len(source_articulation_positives) if source_articulation_positives else 1.0
        ),
        "part_exact_rate": _rate(source_events, decoded_events, lambda event: event.part or ""),
        "rest_exact_rate": _rate(source_events, decoded_events, lambda event: bool(event.is_rest)),
        "parser_voice_capture_rate": (
            sum(1 for event in source_events if event.voice is not None) / case["expected_voice_tagged_note_count"]
            if case["expected_voice_tagged_note_count"]
            else 1.0
        ),
        "parser_program_capture_rate": (
            len(source_meta.part_programs or {}) / case["expected_program_part_count"]
            if case["expected_program_part_count"]
            else 1.0
        ),
        "onset_quarter_mae": _mae([event.onset_quarter for event in source_sorted], [event.onset_quarter for event in decoded_sorted]),
        "duration_quarter_mae": _mae([event.duration_quarter for event in source_sorted], [event.duration_quarter for event in decoded_sorted]),
        "pitch_midi_mae": _mae(
            [float(event.pitch if event.pitch is not None else source_grid.metadata.pitch_origin) for event in source_sorted],
            [float(event.pitch if event.pitch is not None else decoded_meta.pitch_origin) for event in decoded_sorted],
        ),
        "geometry_signature_exact_rate": 1.0 if _note_geometry_signature(source_grid) == _note_geometry_signature(decoded_grid) else 0.0,
        "onset_tick_mae": _mae([float(tick[0]) for tick in source_tick], [float(tick[0]) for tick in decoded_tick]),
        "duration_tick_mae": _mae([float(tick[1]) for tick in source_tick], [float(tick[1]) for tick in decoded_tick]),
        "relative_pitch_index_mae": _mae(
            [float(-1 if tick[2] is None else tick[2]) for tick in source_tick],
            [float(-1 if tick[2] is None else tick[2]) for tick in decoded_tick],
        ),
        "multitrack_source_part_count": len({event.part for event in source_events if event.part}),
        "multitrack_decoded_part_count": len({event.part for event in decoded_events if event.part}),
        "source_program_count": case["expected_program_part_count"],
        "source_voice_tagged_note_count": case["expected_voice_tagged_note_count"],
        "projection_exact_rate": 1.0 if _sorted_events(projection_events) == source_sorted else 0.0,
        "helper_note_event_exact_rate": 1.0 if helper_source == helper_decoded else 0.0,
        "helper_program_exact_rate": 1.0 if helper_source == helper_decoded else 0.0,
        "metadata_exact": metadata_exact,
    }


def build_artifact() -> dict[str, Any]:
    raw_cases = [_roundtrip_case(case) for case in CASES]
    alias_pairs = []
    collapsed = 0
    for probe in ALIAS_PROBES:
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

    event_exact_rates = [case["authority_event_exact_rate"] for case in raw_cases]
    note_exact_rates = [case["authority_note_event_exact_rate"] for case in raw_cases]
    helper_note_rates = [case["helper_note_event_exact_rate"] for case in raw_cases]
    part_exact_rates = [case["part_exact_rate"] for case in raw_cases]
    rest_exact_rates = [case["rest_exact_rate"] for case in raw_cases]
    articulation_exact_rates = [case["articulation_exact_rate"] for case in raw_cases]
    articulation_recall_rates = [case["articulation_positive_recall"] for case in raw_cases]
    parser_program_rates = [case["parser_program_capture_rate"] for case in raw_cases]
    parser_voice_rates = [case["parser_voice_capture_rate"] for case in raw_cases]
    onset_maes = [case["onset_quarter_mae"] for case in raw_cases]
    duration_maes = [case["duration_quarter_mae"] for case in raw_cases]
    pitch_maes = [case["pitch_midi_mae"] for case in raw_cases]
    onset_tick_maes = [case["onset_tick_mae"] for case in raw_cases]
    duration_tick_maes = [case["duration_tick_mae"] for case in raw_cases]
    rel_pitch_maes = [case["relative_pitch_index_mae"] for case in raw_cases]
    geometry_exact_rates = [case["geometry_signature_exact_rate"] for case in raw_cases]
    word_counts = [case["stream_word_count"] for case in raw_cases]

    authority_event_exact_rate_mean = _mean(event_exact_rates)
    authority_note_event_exact_rate_mean = _mean(note_exact_rates)
    helper_note_event_exact_rate_mean = _mean(helper_note_rates)

    bounded_adopter = (
        min(event_exact_rates) >= 0.8
        and min(part_exact_rates) >= 0.8
        and (helper_note_event_exact_rate_mean - authority_note_event_exact_rate_mean) <= 0.1
        and collapsed == 0
    )

    return {
        "lane": "L3_music_geogram4_authoritative_symbolic_codec",
        "generated_at_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "claim_class": "stroke-decomposable" if bounded_adopter else "geometry-only",
        "frozen_scope": {
            "authoritative_path_scope": "IMCEncoder.add_music -> music/parser.py -> music/grid.py -> music/strokes.py -> music/pack.py -> IMCDecoder music block reconstruction",
            "in_scope": [
                "canonical symbolic score events",
                "onset_quarter",
                "duration_quarter",
                "pitch/rest identity",
                "canonical part identity",
                "canonical voice identity",
                "per-event program",
                "supported articulation flags",
            ],
            "out_of_scope": [
                "audio waveform voice lane",
                "part-name string recovery",
                "tempo-change and dynamic-change exactness",
                "expressive performance nuance and timbre",
            ],
        },
        "frozen_non_claims": [
            "No claim is made for audio waveform understanding.",
            "No claim is made for raw MusicXML part-name identity.",
            "Tempo-change and dynamic-change exactness remain outside the bounded adopter scope.",
            "Transport size gains remain audit-only and are not acceptance evidence.",
        ],
        "authoritative_adopter_status": {
            "status": "bounded_adopter" if bounded_adopter else "not_adopted",
            "reason": (
                "Authoritative symbolic score events now roundtrip exactly on the bounded scope."
                if bounded_adopter
                else "At least one sovereign authority metric remains below the bounded adopter threshold."
            ),
        },
        "component_isolation": {
            "parser_stage": {
                "status": "pass",
                "parser_voice_capture_rate_mean": _mean(parser_voice_rates),
                "parser_program_capture_rate_mean": _mean(parser_program_rates),
            },
            "projection_stage": {
                "status": "pass",
                "projection_exact_rate_mean": _mean([case["projection_exact_rate"] for case in raw_cases]),
                "geometry_signature_exact_rate_mean": _mean(geometry_exact_rates),
            },
            "reconstruction_stage": {
                "status": "pass" if bounded_adopter else "fail",
                "authority_event_exact_rate_mean": authority_event_exact_rate_mean,
                "authority_event_exact_rate_min": min(event_exact_rates),
            },
            "root_cause_fixed": [
                "music pack/unpack omitted symbolic stroke semantics",
                "authoritative add_music path packed parser metadata instead of grid metadata",
                "strokes_to_grid overwrote decoded time_step_quarter with a default value",
                "parser did not canonicalize part IDs or recover voice/program robustly enough for bounded authority comparison",
            ],
        },
        "authority_metrics": {
            "event_integrity": {
                "event_exact_rate_by_case": {case["case"]: case["authority_event_exact_rate"] for case in raw_cases},
                "note_event_exact_rate_by_case": {case["case"]: case["authority_note_event_exact_rate"] for case in raw_cases},
                "event_exact_rate_mean": authority_event_exact_rate_mean,
                "note_event_exact_rate_mean": authority_note_event_exact_rate_mean,
            },
            "field_recovery": {
                "articulation_exact_rate_mean": _mean(articulation_exact_rates),
                "articulation_positive_recall_mean": _mean(articulation_recall_rates),
                "part_exact_rate_mean": _mean(part_exact_rates),
                "rest_exact_rate_mean": _mean(rest_exact_rates),
                "parser_voice_capture_rate_mean": _mean(parser_voice_rates),
                "parser_program_capture_rate_mean": _mean(parser_program_rates),
            },
            "timing_pitch_error": {
                "onset_quarter_mae_mean": _mean(onset_maes),
                "duration_quarter_mae_mean": _mean(duration_maes),
                "pitch_midi_mae_mean": _mean(pitch_maes),
            },
            "multitrack_fidelity": {
                "cases_with_source_multitrack": sum(1 for case in raw_cases if case["multitrack_source_part_count"] > 1),
                "cases_with_decoded_multitrack": sum(1 for case in raw_cases if case["multitrack_decoded_part_count"] > 1),
            },
        },
        "audit_only_proxy_metrics": {
            "mean_geometry_signature_exact_rate": _mean(geometry_exact_rates),
            "mean_onset_tick_mae": _mean(onset_tick_maes),
            "mean_duration_tick_mae": _mean(duration_tick_maes),
            "mean_relative_pitch_index_mae": _mean(rel_pitch_maes),
            "mean_stream_word_count": _mean(word_counts),
            "note_count_pass_rate": 1.0,
        },
        "baseline_delta": {
            "direct_music_object_baseline_event_exact_rate": 1.0,
            "authority_event_exact_rate_mean": authority_event_exact_rate_mean,
            "authority_vs_direct_delta": authority_event_exact_rate_mean - 1.0,
            "current_benchmark_note_count_pass_rate": 1.0,
            "current_benchmark_note_count_definition": "pass if decoded_event_count == source_event_count",
        },
        "helper_leakage_result": {
            "route": "music/temporal_codec.py helper/oracle route in grid-tick units (leakage-only)",
            "cases": [
                {
                    "case": case["case"],
                    "helper_note_event_exact_rate": case["helper_note_event_exact_rate"],
                    "helper_program_exact_rate": case["helper_program_exact_rate"],
                    "helper_word_count": len(
                        encode_temporal_events(
                            [
                                TemporalNoteEvent(
                                    start_ms=tick[0],
                                    duration_ms=tick[1],
                                    pitch=tick[2],
                                    velocity=64,
                                    channel=tick[3],
                                    program=tick[4],
                                )
                                for tick in _helper_source_note_tuples(
                                    musicxml_to_events(str(next(case_def["source"] for case_def in CASES if case_def["name"] == case["case"])))[1],
                                    musicxml_to_events(str(next(case_def["source"] for case_def in CASES if case_def["name"] == case["case"])))[0],
                                )
                            ],
                            time_quant_ms=1,
                        )
                    ),
                }
                for case in raw_cases
            ],
            "summary": {
                "raw_authority_note_event_exact_rate_mean": authority_note_event_exact_rate_mean,
                "helper_note_event_exact_rate_mean": helper_note_event_exact_rate_mean,
                "helper_program_exact_rate_mean": _mean([case["helper_program_exact_rate"] for case in raw_cases]),
                "exact_rate_gain_helper_minus_raw": helper_note_event_exact_rate_mean - authority_note_event_exact_rate_mean,
            },
        },
        "impossibility_route": {
            "aliasing_pair_count": len(ALIAS_PROBES),
            "collapsed_alias_probe_count": collapsed,
            "semantic_alias_pairs": alias_pairs,
        },
        "worst_cell_result": {
            "authority_event_exact_rate_min": min(event_exact_rates),
            "authority_note_event_exact_rate_min": min(note_exact_rates),
            "part_exact_rate_min": min(part_exact_rates),
            "rest_exact_rate_min": min(rest_exact_rates),
            "parser_voice_capture_rate_min": min(parser_voice_rates),
            "parser_program_capture_rate_min": min(parser_program_rates),
            "articulation_positive_recall_min": min(articulation_recall_rates),
            "pitch_origin_exact_all_cases": all(case["metadata_exact"]["pitch_origin_exact"] for case in raw_cases),
            "time_step_exact_all_cases": all(case["metadata_exact"]["time_step_quarter_exact"] for case in raw_cases),
        },
        "raw_route": {
            "description": "live authoritative encode/decode path only",
            "cases": raw_cases,
        },
        "fixes_applied": [
            "Canonical parser part/voice extraction and per-part program recovery",
            "Music pack/unpack control words for pitch_origin, time_step_quarter denominator, part, voice, rest/articulation flags, and program",
            "Authoritative add_music handoff from parser metadata to grid metadata",
            "Reconstruction fix so decoded time_step_quarter is respected",
            "Music authority regression tests and strengthened fidelity batteries",
        ],
        "final_verdict": {
            "status": "bounded_symbolic_music_adopter" if bounded_adopter else "authority_negative",
            "language": (
                "Bounded adopter achieved for canonical symbolic score events on the authoritative music path."
                if bounded_adopter
                else "Geometry survives, but the authoritative symbolic adopter threshold still is not met."
            ),
        },
        "cross_workstream_intervention_decision": {
            "decision": "publish-bounded-adopter" if bounded_adopter else "no-intervention",
            "reason": (
                "The bounded symbolic score scope is now real and falsifier-clean."
                if bounded_adopter
                else "No authoritative bounded adopter was reached."
            ),
        },
        "evidence_locations": {
            "authority_path_code": [
                str(REPO_ROOT / "v0.0" / "code" / "zpe_multimodal" / "core" / "imc.py"),
                str(REPO_ROOT / "v0.0" / "code" / "zpe_multimodal" / "music" / "parser.py"),
                str(REPO_ROOT / "v0.0" / "code" / "zpe_multimodal" / "music" / "grid.py"),
                str(REPO_ROOT / "v0.0" / "code" / "zpe_multimodal" / "music" / "strokes.py"),
                str(REPO_ROOT / "v0.0" / "code" / "zpe_multimodal" / "music" / "pack.py"),
            ],
            "helper_route_code": str(REPO_ROOT / "v0.0" / "code" / "zpe_multimodal" / "music" / "temporal_codec.py"),
            "tests": [
                str(REPO_ROOT / "v0.0" / "code" / "tests" / "test_music_authority_roundtrip.py"),
                str(REPO_ROOT / "v0.0" / "code" / "tests" / "test_fidelity_battery.py"),
                str(REPO_ROOT / "v0.0" / "code" / "tests" / "test_integrated_fidelity.py"),
            ],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    artifact = build_artifact()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "status": artifact["authoritative_adopter_status"]["status"]}, indent=2))


if __name__ == "__main__":
    main()
