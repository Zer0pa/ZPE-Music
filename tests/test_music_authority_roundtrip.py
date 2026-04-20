from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests.common import FIXTURES, configure_env

configure_env()

from source.core.imc import IMCDecoder, IMCEncoder
from source.music.grid import grid_to_events
from source.music.parser import musicxml_to_events
from source.music.strokes import strokes_to_grid


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


def _roundtrip_events(source: str | Path) -> tuple[list, list]:
    _meta, source_events = musicxml_to_events(str(source))
    stream = IMCEncoder().add_music(source).build()
    result = IMCDecoder().decode(stream)
    meta, strokes = result.music_blocks[0]
    decoded_events = grid_to_events(strokes_to_grid(strokes, metadata=meta))
    return sorted(source_events, key=_event_key), sorted(decoded_events, key=_event_key)


def _assert_exact_roundtrip(source: str | Path) -> None:
    source_events, decoded_events = _roundtrip_events(source)
    assert decoded_events == source_events


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


def test_simple_scale_authority_roundtrip_exact() -> None:
    _assert_exact_roundtrip(FIXTURES / "simple_scale.musicxml")


def test_multitrack_program_rest_articulation_roundtrip_exact() -> None:
    _assert_exact_roundtrip(REST_ARTICULATION_XML)


def test_voice_tagged_polyphony_roundtrip_exact() -> None:
    _assert_exact_roundtrip(VOICE_TAGGED_POLYPHONY_XML)


def test_tuplet_grid_roundtrip_exact() -> None:
    _assert_exact_roundtrip(TUPLET_GRID_XML)


def test_alias_probes_remain_distinct_on_authority_wire() -> None:
    rest_vs_note = [
        """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1"><part-list><score-part id="P1"><part-name>A</part-name></score-part></part-list><part id="P1"><measure number="1"><attributes><divisions>1</divisions></attributes><note><rest/><duration>1</duration></note></measure></part></score-partwise>""",
        """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1"><part-list><score-part id="P1"><part-name>A</part-name></score-part></part-list><part id="P1"><measure number="1"><attributes><divisions>1</divisions></attributes><note><pitch><step>C</step><octave>4</octave></pitch><duration>1</duration></note></measure></part></score-partwise>""",
    ]
    plain_vs_staccato = [
        """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1"><part-list><score-part id="P1"><part-name>A</part-name></score-part></part-list><part id="P1"><measure number="1"><attributes><divisions>1</divisions></attributes><note><pitch><step>C</step><octave>4</octave></pitch><duration>1</duration></note></measure></part></score-partwise>""",
        """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1"><part-list><score-part id="P1"><part-name>A</part-name></score-part></part-list><part id="P1"><measure number="1"><attributes><divisions>1</divisions></attributes><note><pitch><step>C</step><octave>4</octave></pitch><duration>1</duration><notations><articulations><staccato/></articulations></notations></note></measure></part></score-partwise>""",
    ]
    piano_vs_violin = [
        """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1"><part-list><score-part id="P1"><part-name>A</part-name><score-instrument id="P1-I1"><instrument-name>Piano</instrument-name></score-instrument><midi-instrument id="P1-I1"><midi-program>1</midi-program></midi-instrument></score-part></part-list><part id="P1"><measure number="1"><attributes><divisions>1</divisions></attributes><note><pitch><step>C</step><octave>4</octave></pitch><duration>1</duration></note></measure></part></score-partwise>""",
        """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1"><part-list><score-part id="P1"><part-name>A</part-name><score-instrument id="P1-I1"><instrument-name>Violin</instrument-name></score-instrument><midi-instrument id="P1-I1"><midi-program>41</midi-program></midi-instrument></score-part></part-list><part id="P1"><measure number="1"><attributes><divisions>1</divisions></attributes><note><pitch><step>C</step><octave>4</octave></pitch><duration>1</duration></note></measure></part></score-partwise>""",
    ]
    part_assignment = [
        """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1">
  <part-list>
    <score-part id="P1"><part-name>P1</part-name></score-part>
    <score-part id="P2"><part-name>P2</part-name></score-part>
  </part-list>
  <part id="P1"><measure number="1"><attributes><divisions>1</divisions></attributes><note><pitch><step>C</step><octave>4</octave></pitch><duration>1</duration></note></measure></part>
  <part id="P2"><measure number="1"><attributes><divisions>1</divisions></attributes><note><pitch><step>G</step><octave>4</octave></pitch><duration>1</duration></note></measure></part>
</score-partwise>""",
        """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1">
  <part-list>
    <score-part id="P1"><part-name>P1</part-name></score-part>
    <score-part id="P2"><part-name>P2</part-name></score-part>
  </part-list>
  <part id="P1"><measure number="1"><attributes><divisions>1</divisions></attributes><note><pitch><step>G</step><octave>4</octave></pitch><duration>1</duration></note></measure></part>
  <part id="P2"><measure number="1"><attributes><divisions>1</divisions></attributes><note><pitch><step>C</step><octave>4</octave></pitch><duration>1</duration></note></measure></part>
</score-partwise>""",
    ]

    for left, right in (rest_vs_note, plain_vs_staccato, piano_vs_violin, part_assignment):
        assert IMCEncoder().add_music(left).build() != IMCEncoder().add_music(right).build()
