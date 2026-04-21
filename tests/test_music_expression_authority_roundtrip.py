from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests.common import configure_env

configure_env()

from zpe_music.core.imc import IMCDecoder, IMCEncoder
from zpe_music.music.grid import grid_to_events
from zpe_music.music.parser import musicxml_to_events
from zpe_music.music.strokes import strokes_to_grid


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


def _roundtrip_events(source: str) -> tuple[list, list]:
    _meta, source_events = musicxml_to_events(source)
    stream = IMCEncoder().add_music(source).build()
    result = IMCDecoder().decode(stream)
    meta, strokes = result.music_blocks[0]
    decoded_events = grid_to_events(strokes_to_grid(strokes, metadata=meta))
    return sorted(source_events, key=_event_key), sorted(decoded_events, key=_event_key)


def _assert_exact_roundtrip(source: str) -> None:
    source_events, decoded_events = _roundtrip_events(source)
    assert decoded_events == source_events


EXPRESSION_XML = """<?xml version="1.0" encoding="UTF-8"?>
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
      <note dynamics="72" attack="-1" release="2">
        <pitch><step>C</step><octave>4</octave></pitch>
        <duration>12</duration>
      </note>
      <note dynamics="91" attack="2" release="-1">
        <pitch><step>D</step><octave>4</octave></pitch>
        <duration>12</duration>
      </note>
      <note dynamics="58" attack="0" release="1">
        <pitch><step>E</step><octave>4</octave></pitch>
        <duration>12</duration>
      </note>
      <note dynamics="103" attack="-2" release="0">
        <pitch><step>F</step><octave>4</octave></pitch>
        <duration>12</duration>
      </note>
    </measure>
  </part>
</score-partwise>
"""


REPEATED_NOTE_XML = """<?xml version="1.0" encoding="UTF-8"?>
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
      <note dynamics="48" attack="-1" release="0">
        <pitch><step>C</step><octave>4</octave></pitch>
        <duration>6</duration>
      </note>
      <note dynamics="96" attack="2" release="-2">
        <pitch><step>C</step><octave>4</octave></pitch>
        <duration>6</duration>
      </note>
      <note dynamics="63" attack="0" release="1">
        <pitch><step>C</step><octave>4</octave></pitch>
        <duration>6</duration>
      </note>
      <note dynamics="84" attack="-2" release="2">
        <pitch><step>C</step><octave>4</octave></pitch>
        <duration>6</duration>
      </note>
    </measure>
  </part>
</score-partwise>
"""


TUPLET_EXPRESSION_XML = """<?xml version="1.0" encoding="UTF-8"?>
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
      <note dynamics="67" attack="-1" release="1">
        <pitch><step>C</step><octave>4</octave></pitch>
        <duration>4</duration>
      </note>
      <note dynamics="74" attack="1" release="0">
        <pitch><step>D</step><octave>4</octave></pitch>
        <duration>4</duration>
      </note>
      <note dynamics="81" attack="0" release="-1">
        <pitch><step>E</step><octave>4</octave></pitch>
        <duration>4</duration>
      </note>
      <note dynamics="52" attack="0" release="0">
        <rest/>
        <duration>6</duration>
      </note>
      <note dynamics="95" attack="-2" release="2">
        <pitch><step>F</step><octave>4</octave></pitch>
        <duration>6</duration>
      </note>
    </measure>
  </part>
</score-partwise>
"""


def test_expression_roundtrip_exact() -> None:
    _assert_exact_roundtrip(EXPRESSION_XML)


def test_expression_parser_extracts_score_anchored_fields() -> None:
    _meta, events = musicxml_to_events(EXPRESSION_XML)
    assert [
        (
            event.pitch,
            event.performance_onset_quarter_delta,
            event.performance_duration_quarter_delta,
            event.velocity,
        )
        for event in sorted(events, key=_event_key)
    ] == [
        (60, -1 / 12, 3 / 12, 72),
        (62, 2 / 12, -3 / 12, 91),
        (64, 0.0, 1 / 12, 58),
        (65, -2 / 12, 2 / 12, 103),
    ]


def test_repeated_note_expression_roundtrip_exact() -> None:
    _assert_exact_roundtrip(REPEATED_NOTE_XML)


def test_tuplet_expression_roundtrip_exact() -> None:
    _assert_exact_roundtrip(TUPLET_EXPRESSION_XML)


def test_expression_alias_probes_remain_distinct_on_authority_wire() -> None:
    velocity_pair = [
        """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1"><part-list><score-part id="P1"><part-name>A</part-name></score-part></part-list><part id="P1"><measure number="1"><attributes><divisions>12</divisions></attributes><note dynamics="48"><pitch><step>C</step><octave>4</octave></pitch><duration>12</duration></note></measure></part></score-partwise>""",
        """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1"><part-list><score-part id="P1"><part-name>A</part-name></score-part></part-list><part id="P1"><measure number="1"><attributes><divisions>12</divisions></attributes><note dynamics="96"><pitch><step>C</step><octave>4</octave></pitch><duration>12</duration></note></measure></part></score-partwise>""",
    ]
    onset_pair = [
        """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1"><part-list><score-part id="P1"><part-name>A</part-name></score-part></part-list><part id="P1"><measure number="1"><attributes><divisions>12</divisions></attributes><note attack="-2"><pitch><step>C</step><octave>4</octave></pitch><duration>12</duration></note></measure></part></score-partwise>""",
        """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1"><part-list><score-part id="P1"><part-name>A</part-name></score-part></part-list><part id="P1"><measure number="1"><attributes><divisions>12</divisions></attributes><note attack="2"><pitch><step>C</step><octave>4</octave></pitch><duration>12</duration></note></measure></part></score-partwise>""",
    ]
    duration_pair = [
        """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1"><part-list><score-part id="P1"><part-name>A</part-name></score-part></part-list><part id="P1"><measure number="1"><attributes><divisions>12</divisions></attributes><note attack="0" release="-2"><pitch><step>C</step><octave>4</octave></pitch><duration>12</duration></note></measure></part></score-partwise>""",
        """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1"><part-list><score-part id="P1"><part-name>A</part-name></score-part></part-list><part id="P1"><measure number="1"><attributes><divisions>12</divisions></attributes><note attack="0" release="2"><pitch><step>C</step><octave>4</octave></pitch><duration>12</duration></note></measure></part></score-partwise>""",
    ]

    for left, right in (velocity_pair, onset_pair, duration_pair):
        assert IMCEncoder().add_music(left).build() != IMCEncoder().add_music(right).build()
