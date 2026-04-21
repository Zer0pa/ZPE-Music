from __future__ import annotations

from fractions import Fraction
from math import gcd
from typing import Iterable, List, Optional, Sequence

from .types import GridNote, MusicGrid, MusicMetadata, NoteEvent


def _lcm(a: int, b: int) -> int:
    return abs(a * b) // gcd(a, b) if a and b else 0


def _infer_time_step(events: Sequence[NoteEvent], limit_denominator: int = 1024) -> float:
    """Choose a grid step that captures tuplets by using LCM of denominators."""
    denom = 1
    for ev in events:
        onset = Fraction(ev.onset_quarter).limit_denominator(limit_denominator)
        dur = Fraction(ev.duration_quarter).limit_denominator(limit_denominator)
        denom = _lcm(denom, onset.denominator)
        denom = _lcm(denom, dur.denominator)
        if ev.performance_onset_quarter_delta is not None:
            perf_onset = Fraction(ev.performance_onset_quarter_delta).limit_denominator(limit_denominator)
            denom = _lcm(denom, perf_onset.denominator)
        if ev.performance_duration_quarter_delta is not None:
            perf_duration = Fraction(ev.performance_duration_quarter_delta).limit_denominator(limit_denominator)
            denom = _lcm(denom, perf_duration.denominator)
    if denom == 0:
        denom = 1
    return 1.0 / denom


def events_to_grid(
    events: Sequence[NoteEvent],
    metadata: MusicMetadata,
    time_step_quarter: Optional[float] = None,
    pitch_origin: Optional[int] = None,
) -> MusicGrid:
    """Quantize note/rest events into a time×pitch grid."""
    if time_step_quarter is None:
        time_step_quarter = _infer_time_step(events)

    origin = (
        pitch_origin
        if pitch_origin is not None
        else min((e.pitch for e in events if e.pitch is not None), default=0)
    )
    grid_notes: List[GridNote] = []
    for ev in events:
        start_tick = int(round(ev.onset_quarter / time_step_quarter))
        duration_ticks = max(1, int(round(ev.duration_quarter / time_step_quarter)))
        grid_notes.append(
            GridNote(
                start_tick=start_tick,
                duration_ticks=duration_ticks,
                pitch=ev.pitch,
                part=ev.part,
                voice=ev.voice,
                program=ev.program,
                is_rest=ev.is_rest,
                articulations=ev.articulations,
                performance_onset_tick_delta=(
                    None
                    if ev.performance_onset_quarter_delta is None
                    else int(round(ev.performance_onset_quarter_delta / time_step_quarter))
                ),
                performance_duration_tick_delta=(
                    None
                    if ev.performance_duration_quarter_delta is None
                    else int(round(ev.performance_duration_quarter_delta / time_step_quarter))
                ),
                velocity=ev.velocity,
            )
        )

    grid_meta = metadata.with_pitch_origin(origin).with_time_step(time_step_quarter)
    return MusicGrid(notes=grid_notes, metadata=grid_meta)


def grid_to_events(grid: MusicGrid) -> List[NoteEvent]:
    """Convert a grid back into quarter-length note/rest events."""
    step = grid.metadata.time_step_quarter
    origin = grid.metadata.pitch_origin
    events: List[NoteEvent] = []
    for note in grid.notes:
        onset_quarter = float(note.start_tick * step)
        duration_quarter = float(note.duration_ticks * step)
        pitch = None if note.pitch is None else int(note.pitch)
        events.append(
            NoteEvent(
                onset_quarter=onset_quarter,
                duration_quarter=duration_quarter,
                pitch=pitch,
                part=note.part,
                voice=note.voice,
                program=note.program,
                is_rest=note.is_rest,
                articulations=note.articulations,
                performance_onset_quarter_delta=(
                    None
                    if note.performance_onset_tick_delta is None
                    else float(note.performance_onset_tick_delta * step)
                ),
                performance_duration_quarter_delta=(
                    None
                    if note.performance_duration_tick_delta is None
                    else float(note.performance_duration_tick_delta * step)
                ),
                velocity=note.velocity,
            )
        )
    return events
