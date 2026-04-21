from __future__ import annotations

from typing import Iterable, List, Sequence

from ..diagram.quantize import DIRS, DrawDir, MoveTo
from .grid import grid_to_events
from .types import GridNote, MusicGrid, MusicMetadata, MusicStroke


def grid_to_strokes(grid: MusicGrid) -> List[MusicStroke]:
    """Convert a MusicGrid into stroke paths (MoveTo + horizontal draws)."""
    strokes: List[MusicStroke] = []
    origin = grid.metadata.pitch_origin
    for note in sorted(grid.notes, key=lambda n: (n.start_tick, n.pitch or -1)):
        y = 0 if note.pitch is None else note.pitch - origin
        commands = [MoveTo(note.start_tick, y)]
        for _ in range(max(1, note.duration_ticks)):
            commands.append(DrawDir(0))  # R (time-forward at fixed pitch)
        strokes.append(
            MusicStroke(
                commands=commands,
                part=note.part,
                voice=note.voice,
                pitch=note.pitch,
                program=note.program,
                is_rest=note.is_rest,
                articulations=note.articulations,
                performance_onset_tick_delta=note.performance_onset_tick_delta,
                performance_duration_tick_delta=note.performance_duration_tick_delta,
                velocity=note.velocity,
            )
        )
    return strokes


def strokes_to_grid(
    strokes: Sequence[MusicStroke],
    time_step_quarter: float | None = None,
    pitch_origin: int | None = None,
    metadata: MusicMetadata | None = None,
) -> MusicGrid:
    """Reconstruct a MusicGrid from stroke paths."""
    origin = pitch_origin
    if origin is None and metadata is not None:
        origin = metadata.pitch_origin
    if origin is None:
        origin = 0
    if time_step_quarter is None:
        time_step_quarter = metadata.time_step_quarter if metadata is not None else 0.25

    grid_notes: List[GridNote] = []
    for stroke in strokes:
        start_tick = None
        start_pitch_idx = 0
        time_pos = 0
        pitch_idx = 0
        duration = 0
        for cmd in stroke.commands:
            if isinstance(cmd, MoveTo):
                start_tick = cmd.x
                time_pos = cmd.x
                pitch_idx = cmd.y
                start_pitch_idx = cmd.y
            elif isinstance(cmd, DrawDir):
                dx, dy = DIRS[cmd.direction]
                time_pos += dx
                pitch_idx += dy
                if dx > 0:
                    duration += dx
            else:  # pragma: no cover - defensive
                raise TypeError(f"unexpected stroke command {cmd!r}")
        if start_tick is None:
            continue
        if duration <= 0:
            duration = 1
        pitch_value = None if stroke.is_rest else origin + start_pitch_idx
        grid_notes.append(
            GridNote(
                start_tick=int(start_tick),
                duration_ticks=int(duration),
                pitch=pitch_value,
                part=stroke.part,
                voice=stroke.voice,
                program=stroke.program,
                is_rest=stroke.is_rest,
                articulations=stroke.articulations,
                performance_onset_tick_delta=stroke.performance_onset_tick_delta,
                performance_duration_tick_delta=stroke.performance_duration_tick_delta,
                velocity=stroke.velocity,
            )
        )

    grid_meta = (
        metadata.with_pitch_origin(origin).with_time_step(time_step_quarter)
        if metadata
        else MusicMetadata(pitch_origin=origin, time_step_quarter=time_step_quarter)
    )
    return MusicGrid(notes=grid_notes, metadata=grid_meta)
