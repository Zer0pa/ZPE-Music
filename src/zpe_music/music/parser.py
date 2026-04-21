from __future__ import annotations

import os
import xml.etree.ElementTree as ET
from typing import Dict, Iterable, List, Tuple

from .types import MusicMetadata, NoteEvent


def _require_music21():
    try:
        import music21  # type: ignore
    except ImportError as exc:  # pragma: no cover - exercised when missing dependency
        raise ImportError(
            "music21 is required for Tier-3A music support. Install via `pip install music21`."
        ) from exc
    return music21


def _load_score(source: str):
    music21 = _require_music21()
    # Path on disk takes priority; otherwise treat as inline XML.
    if os.path.exists(source):
        return music21.converter.parse(source)
    if source.lstrip().startswith("<"):
        return music21.converter.parseData(source, format="musicxml")
    return music21.converter.parse(source)


def _extract_metadata(score) -> MusicMetadata:
    music21 = _require_music21()
    time_signature = None
    key_signature = None
    tempo = None
    tempo_changes = []
    dynamic_changes = []
    part_names = {}
    part_programs = {}

    ts = score.recurse().getElementsByClass(music21.meter.TimeSignature)
    first_ts = next(iter(ts), None)
    if first_ts:
        time_signature = (int(first_ts.numerator), int(first_ts.denominator))

    ks = score.recurse().getElementsByClass(music21.key.KeySignature)
    first_ks = next(iter(ks), None)
    if first_ks is not None:
        key_signature = int(first_ks.sharps)

    tempos = score.recurse().getElementsByClass(music21.tempo.MetronomeMark)
    first_tempo = next(iter(tempos), None)
    if first_tempo and first_tempo.number is not None:
        tempo = float(first_tempo.number)
    for tmark in tempos:
        if tmark.number is None:
            continue
        tempo_changes.append((float(tmark.offset), float(tmark.number)))

    dyns = score.recurse().getElementsByClass(music21.dynamics.Dynamic)
    for d in dyns:
        if getattr(d, "value", None):
            dynamic_changes.append((float(d.offset), str(d.value)))

    for idx, part in enumerate(score.parts):
        part_id = _canonical_part_id(idx)
        name = getattr(part, "partName", None) or part_id
        part_names[part_id] = str(name)
        program = _extract_part_program(part)
        if program is not None:
            part_programs[part_id] = int(program)

    return MusicMetadata(
        time_signature=time_signature,
        key_signature=key_signature,
        tempo=tempo,
        tempo_changes=tempo_changes or None,
        dynamic_changes=dynamic_changes or None,
        part_names=part_names or None,
        part_programs=part_programs or None,
    )


def _canonical_part_id(index: int) -> str:
    return f"P{index + 1}"


def _canonical_voice_id(label: str | None, voice_map: Dict[str, str]) -> str | None:
    if label is None:
        return None
    cleaned = str(label).strip()
    if not cleaned:
        return None
    if cleaned not in voice_map:
        digits = "".join(ch for ch in cleaned if ch.isdigit())
        if digits:
            voice_map[cleaned] = f"V{int(digits)}"
        else:
            voice_map[cleaned] = f"V{len(voice_map) + 1}"
    return voice_map[cleaned]


def _extract_part_program(part) -> int | None:
    music21 = _require_music21()
    for instrument in part.recurse().getElementsByClass(music21.instrument.Instrument):
        program = getattr(instrument, "midiProgram", None)
        if program is not None:
            return int(program)
    instrument = part.getInstrument(returnDefault=False)
    if instrument is None:
        return None
    program = getattr(instrument, "midiProgram", None)
    return None if program is None else int(program)


def _extract_voice_label(element, music21) -> str | None:
    voice = getattr(element, "voice", None)
    if voice not in (None, ""):
        return str(voice)

    context = element.getContextByClass(music21.stream.Voice)
    if context is not None:
        for attr in ("id", "number"):
            value = getattr(context, attr, None)
            if value not in (None, ""):
                return str(value)

    active_site = getattr(element, "activeSite", None)
    if isinstance(active_site, music21.stream.Voice):
        for attr in ("id", "number"):
            value = getattr(active_site, attr, None)
            if value not in (None, ""):
                return str(value)
    return None


def _load_xml_root(source: str):
    if os.path.exists(source):
        return ET.parse(source).getroot()
    if source.lstrip().startswith("<"):
        return ET.fromstring(source)
    raise ValueError("musicxml_to_events expects a path or inline MusicXML")


def _strip_ns(tag: str) -> str:
    return tag.split("}", 1)[-1]


def _parse_int(value: str | None) -> int | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return int(text)
    except ValueError:
        return None


def _parse_pitch(note_elem) -> int | None:
    pitch_elem = None
    for child in note_elem:
        if _strip_ns(child.tag) == "pitch":
            pitch_elem = child
            break
    if pitch_elem is None:
        return None
    values = {}
    for child in pitch_elem:
        values[_strip_ns(child.tag)] = (child.text or "").strip()
    step = values.get("step", "C").upper()
    octave = _parse_int(values.get("octave"))
    if octave is None:
        return None
    alter = _parse_int(values.get("alter")) or 0
    semitone = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}.get(step, 0)
    return int((octave + 1) * 12 + semitone + alter)


def _extract_articulations_xml(note_elem) -> list[str] | None:
    names: list[str] = []
    xml_to_name = {
        "staccato": "Staccato",
        "accent": "Accent",
        "tenuto": "Tenuto",
        "strong-accent": "Marcato",
        "marcato": "Marcato",
    }
    for child in note_elem:
        if _strip_ns(child.tag) != "notations":
            continue
        for notation_child in child:
            if _strip_ns(notation_child.tag) != "articulations":
                continue
            for art_child in notation_child:
                art_name = xml_to_name.get(_strip_ns(art_child.tag))
                if art_name and art_name not in names:
                    names.append(art_name)
    return names or None


def _extract_tie_type_xml(note_elem) -> str | None:
    for child in note_elem:
        if _strip_ns(child.tag) != "tie":
            continue
        tie_type = child.attrib.get("type")
        if tie_type:
            return str(tie_type)
    for child in note_elem:
        if _strip_ns(child.tag) != "notations":
            continue
        for notation_child in child:
            if _strip_ns(notation_child.tag) != "tied":
                continue
            tie_type = notation_child.attrib.get("type")
            if tie_type:
                return str(tie_type)
    return None


def _extract_expression_xml(note_elem, divisions: int) -> tuple[float | None, float | None, int | None]:
    attack = _parse_int(note_elem.attrib.get("attack"))
    release = _parse_int(note_elem.attrib.get("release"))
    dynamics = _parse_int(note_elem.attrib.get("dynamics"))
    onset_delta = None if attack is None else float(attack / max(1, divisions))
    release_delta = None if release is None else float(release / max(1, divisions))
    duration_delta = None
    if onset_delta is not None or release_delta is not None:
        duration_delta = float((release_delta or 0.0) - (onset_delta or 0.0))
    return onset_delta, duration_delta, dynamics


def _events_from_xml_source(source: str, metadata: MusicMetadata) -> List[NoteEvent]:
    root = _load_xml_root(source)
    part_elems = [child for child in root if _strip_ns(child.tag) == "part"]
    events: List[NoteEvent] = []

    for part_index, part_elem in enumerate(part_elems):
        part_id = _canonical_part_id(part_index)
        part_program = None if metadata.part_programs is None else metadata.part_programs.get(part_id)
        voice_map: Dict[str, str] = {}
        divisions = 1
        current_div_pos = 0
        last_note_start_div = 0

        for measure_elem in part_elem:
            if _strip_ns(measure_elem.tag) != "measure":
                continue
            current_div_pos = 0
            last_note_start_div = 0
            for child in measure_elem:
                tag = _strip_ns(child.tag)
                if tag == "attributes":
                    for attr_child in child:
                        if _strip_ns(attr_child.tag) == "divisions":
                            divisions = max(1, _parse_int(attr_child.text) or 1)
                    continue
                if tag == "backup":
                    current_div_pos -= _parse_int(child.findtext("./duration")) or 0
                    continue
                if tag == "forward":
                    current_div_pos += _parse_int(child.findtext("./duration")) or 0
                    continue
                if tag != "note":
                    continue

                duration_div = max(0, _parse_int(child.findtext("./duration")) or 0)
                is_chord = any(_strip_ns(grand.tag) == "chord" for grand in child)
                onset_div = last_note_start_div if is_chord else current_div_pos
                if not is_chord:
                    last_note_start_div = onset_div
                if not is_chord:
                    current_div_pos += duration_div

                voice_raw = child.findtext("./voice")
                voice_id = _canonical_voice_id(voice_raw, voice_map)
                articulations = _extract_articulations_xml(child)
                tie_type = _extract_tie_type_xml(child)
                onset_delta, duration_delta, dynamics = _extract_expression_xml(child, divisions)
                is_rest = child.find("./rest") is not None
                pitch = None if is_rest else _parse_pitch(child)
                duration_quarter = float(duration_div / max(1, divisions))
                onset_quarter = float(onset_div / max(1, divisions))
                events.append(
                    NoteEvent(
                        onset_quarter=onset_quarter,
                        duration_quarter=duration_quarter,
                        pitch=pitch,
                        part=part_id,
                        voice=voice_id,
                        program=part_program,
                        is_rest=is_rest,
                        tie_type=tie_type,
                        articulations=articulations,
                        performance_onset_quarter_delta=onset_delta,
                        performance_duration_quarter_delta=duration_delta,
                        velocity=dynamics,
                    )
                )
    return events


def _event_offset_in_part(element, part) -> float:
    try:
        return float(element.getOffsetInHierarchy(part))
    except Exception:  # pragma: no cover - defensive fallback
        return float(element.offset)


def _events_from_part(part, part_id: str, part_program: int | None = None) -> Iterable[NoteEvent]:
    music21 = _require_music21()
    voice_map: Dict[str, str] = {}
    for element in part.recurse().notesAndRests:
        onset = _event_offset_in_part(element, part)
        duration = float(element.duration.quarterLength)
        voice_id = _canonical_voice_id(_extract_voice_label(element, music21), voice_map)
        articulations = None
        if getattr(element, "articulations", None):
            articulations = list(dict.fromkeys(type(a).__name__ for a in element.articulations))

        if element.isRest:
            yield NoteEvent(
                onset_quarter=onset,
                duration_quarter=duration,
                pitch=None,
                part=part_id,
                voice=voice_id,
                program=part_program,
                is_rest=True,
                tie_type=None,
                articulations=articulations,
            )
        elif element.isChord:
            # Flatten each pitch in the chord into its own event.
            for pitch in element.pitches:
                yield NoteEvent(
                    onset_quarter=onset,
                    duration_quarter=duration,
                    pitch=int(pitch.midi),
                    part=part_id,
                    voice=voice_id,
                    program=part_program,
                    is_rest=False,
                    tie_type=getattr(element.tie, "type", None),
                    articulations=articulations,
                )
        elif element.isNote:
            tie_type = getattr(element.tie, "type", None)
            yield NoteEvent(
                onset_quarter=onset,
                duration_quarter=duration,
                pitch=int(element.pitch.midi),
                part=part_id,
                voice=voice_id,
                program=part_program,
                is_rest=False,
                tie_type=tie_type,
                articulations=articulations,
            )


def musicxml_to_events(source: str) -> Tuple[MusicMetadata, List[NoteEvent]]:
    """Parse MusicXML (path or inline XML) into note/rest events + metadata."""
    score = _load_score(source)
    metadata = _extract_metadata(score)
    events = _events_from_xml_source(source, metadata)
    events = _merge_ties(events)
    return metadata, events


def _merge_ties(events: List[NoteEvent]) -> List[NoteEvent]:
    """Merge tie chains into single events to stabilize quantization."""
    merged: List[NoteEvent] = []
    active = {}
    # Sort by part/voice/pitch/onset to keep chains adjacent.
    events_sorted = sorted(
        events,
        key=lambda e: (e.part or "", e.voice or "", e.pitch if e.pitch is not None else -1, e.onset_quarter),
    )
    for ev in events_sorted:
        if ev.is_rest or ev.pitch is None:
            merged.append(ev)
            continue
        key = (ev.part or "", ev.voice or "", ev.pitch)
        tie_type = (ev.tie_type or "").lower() if ev.tie_type else None
        if tie_type in ("start", "continue"):
            if key in active:
                onset, dur, arts, program, perf_onset, perf_release, velocity = active[key]
                current_release = None
                if ev.performance_onset_quarter_delta is not None or ev.performance_duration_quarter_delta is not None:
                    current_release = (ev.performance_onset_quarter_delta or 0.0) + (ev.performance_duration_quarter_delta or 0.0)
                active[key] = (
                    onset,
                    dur + ev.duration_quarter,
                    _merge_artics(arts, ev.articulations),
                    program,
                    perf_onset,
                    current_release if current_release is not None else perf_release,
                    velocity if velocity is not None else ev.velocity,
                )
            else:
                release_delta = None
                if ev.performance_onset_quarter_delta is not None or ev.performance_duration_quarter_delta is not None:
                    release_delta = (ev.performance_onset_quarter_delta or 0.0) + (ev.performance_duration_quarter_delta or 0.0)
                active[key] = (
                    ev.onset_quarter,
                    ev.duration_quarter,
                    ev.articulations,
                    ev.program,
                    ev.performance_onset_quarter_delta,
                    release_delta,
                    ev.velocity,
                )
            continue
        if tie_type in ("stop", "end"):
            if key in active:
                onset, dur, arts, program, perf_onset, perf_release, velocity = active.pop(key)
                current_release = None
                if ev.performance_onset_quarter_delta is not None or ev.performance_duration_quarter_delta is not None:
                    current_release = (ev.performance_onset_quarter_delta or 0.0) + (ev.performance_duration_quarter_delta or 0.0)
                merged_release = current_release if current_release is not None else perf_release
                merged_duration_delta = None
                if perf_onset is not None or merged_release is not None:
                    merged_duration_delta = (merged_release or 0.0) - (perf_onset or 0.0)
                merged.append(
                    NoteEvent(
                        onset_quarter=onset,
                        duration_quarter=dur + ev.duration_quarter,
                        pitch=ev.pitch,
                        part=ev.part,
                        voice=ev.voice,
                        program=program,
                        is_rest=False,
                        tie_type=None,
                        articulations=_merge_artics(arts, ev.articulations),
                        performance_onset_quarter_delta=perf_onset,
                        performance_duration_quarter_delta=merged_duration_delta,
                        velocity=velocity if velocity is not None else ev.velocity,
                    )
                )
                continue
        # No tie: flush any active chain then add this event.
        if key in active:
            onset, dur, arts, program, perf_onset, perf_release, velocity = active.pop(key)
            merged_duration_delta = None
            if perf_onset is not None or perf_release is not None:
                merged_duration_delta = (perf_release or 0.0) - (perf_onset or 0.0)
            merged.append(
                NoteEvent(
                    onset_quarter=onset,
                    duration_quarter=dur,
                    pitch=ev.pitch,
                    part=ev.part,
                    voice=ev.voice,
                    program=program,
                    is_rest=False,
                    tie_type=None,
                    articulations=arts,
                    performance_onset_quarter_delta=perf_onset,
                    performance_duration_quarter_delta=merged_duration_delta,
                    velocity=velocity,
                )
            )
        merged.append(ev)

    for (part, voice, pitch), (onset, dur, arts, program, perf_onset, perf_release, velocity) in active.items():
        merged_duration_delta = None
        if perf_onset is not None or perf_release is not None:
            merged_duration_delta = (perf_release or 0.0) - (perf_onset or 0.0)
        merged.append(
            NoteEvent(
                onset_quarter=onset,
                duration_quarter=dur,
                pitch=pitch,
                part=part or None,
                voice=voice or None,
                program=program,
                is_rest=False,
                tie_type=None,
                articulations=arts,
                performance_onset_quarter_delta=perf_onset,
                performance_duration_quarter_delta=merged_duration_delta,
                velocity=velocity,
            )
        )
    return merged


def _merge_artics(a, b):
    if not a:
        return b
    if not b:
        return a
    merged = list(dict.fromkeys(list(a) + list(b)))
    return merged
