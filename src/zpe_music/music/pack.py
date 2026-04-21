from __future__ import annotations

from dataclasses import replace
from fractions import Fraction
from typing import Iterable, List

from ..core.constants import DEFAULT_VERSION, Mode
from .flags import music_enabled
from .types import MusicMetadata, MusicStroke
from ..diagram.quantize import DrawDir, MoveTo

# Extension payload bit 14 flags music blocks (bit 15 used by diagrams).
MUSIC_TYPE_BIT = 0x4000
# Collision-safe subtype layout in low payload bits [11..10].
SUBTYPE_BOUNDARY = 0
SUBTYPE_MOVE_T = 1
SUBTYPE_MOVE_P = 2
SUBTYPE_DRAW_RUN = 3
SUBTYPE_SHIFT = 10
SUBTYPE_MASK = 0x3

CANVAS_LIMIT = 0x3FF  # 10 bits for positions/run payloads
MAX_RUN = 0x7F        # run shares payload with 3-bit direction

META_FLAG = 1 << 9
META_KIND_SHIFT = 7
META_KIND_MASK = 0x3
META_VALUE_MASK = 0x7F

META_KIND_TIMESIG = 0
META_KIND_KEY = 1
META_KIND_TEMPO = 2
META_KIND_DYNAMIC = 3

# Control words are represented as SUBTYPE_MOVE_T when no immediate MoveP follows.
CTRL_TAG_SHIFT = 7
CTRL_TAG_MASK = 0x7
CTRL_VALUE_MASK = 0x7F
CTRL_TAG_TIME_ANCHOR = 0
CTRL_TAG_PITCH_ORIGIN = 1
CTRL_TAG_TIME_STEP_DEN = 2
CTRL_TAG_PART_INDEX = 3
CTRL_TAG_VOICE_INDEX = 4
CTRL_TAG_FLAGS = 5
CTRL_TAG_PROGRAM = 6
CTRL2_TAG_SHIFT = 7
CTRL2_TAG_MASK = 0x7
CTRL2_VALUE_MASK = 0x7F
CTRL2_TAG_PERF_ONSET_DELTA = 0
CTRL2_TAG_PERF_DURATION_DELTA = 1
CTRL2_TAG_VELOCITY = 2
SIGNED_CTRL2_BIAS = 64

FLAG_IS_REST = 1 << 0
FLAG_STACCATO = 1 << 1
FLAG_ACCENT = 1 << 2
FLAG_TENUTO = 1 << 3
FLAG_MARCATO = 1 << 4

ARTICULATION_FLAGS = {
    "Staccato": FLAG_STACCATO,
    "Accent": FLAG_ACCENT,
    "Tenuto": FLAG_TENUTO,
    "Marcato": FLAG_MARCATO,
}
FLAG_TO_ARTICULATION = (
    (FLAG_STACCATO, "Staccato"),
    (FLAG_ACCENT, "Accent"),
    (FLAG_TENUTO, "Tenuto"),
    (FLAG_MARCATO, "Marcato"),
)


def _ext_word(payload: int) -> int:
    return (Mode.EXTENSION.value << 18) | (DEFAULT_VERSION << 16) | payload


def _with_subtype(subtype: int, data: int) -> int:
    return MUSIC_TYPE_BIT | ((subtype & SUBTYPE_MASK) << SUBTYPE_SHIFT) | data


def _control_data(tag: int, value: int) -> int:
    return ((tag & CTRL_TAG_MASK) << CTRL_TAG_SHIFT) | (value & CTRL_VALUE_MASK)


def _emit_control(words: List[int], tag: int, value: int) -> None:
    words.append(_ext_word(_with_subtype(SUBTYPE_MOVE_T, _control_data(tag, value))))


def _control2_data(tag: int, value: int) -> int:
    return ((tag & CTRL2_TAG_MASK) << CTRL2_TAG_SHIFT) | (value & CTRL2_VALUE_MASK)


def _emit_control2(words: List[int], tag: int, value: int) -> None:
    words.append(_ext_word(_with_subtype(SUBTYPE_MOVE_P, _control2_data(tag, value))))


def _clamp_anchor(value: int | None) -> int | None:
    if value is None:
        return None
    return max(0, min(CTRL_VALUE_MASK, int(value)))


def _clamp_small(value: int | None, *, minimum: int = 0, maximum: int = CTRL_VALUE_MASK) -> int | None:
    if value is None:
        return None
    return max(minimum, min(maximum, int(value)))


def _encode_signed_small(value: int | None) -> int | None:
    if value is None:
        return None
    signed = int(value)
    if not (-SIGNED_CTRL2_BIAS <= signed <= SIGNED_CTRL2_BIAS - 1):
        raise ValueError(f"signed music control out of range: {signed}")
    return signed + SIGNED_CTRL2_BIAS


def _decode_signed_small(value: int) -> int:
    return int(value) - SIGNED_CTRL2_BIAS


def _canonical_label_index(label: object, prefix: str) -> int | None:
    text = str(label).strip()
    if not text:
        return None
    if text.startswith(prefix) and text[len(prefix) :].isdigit():
        return int(text[len(prefix) :])
    if text.isdigit():
        return int(text)
    return None


def _build_label_registry(labels: Iterable[object | None], prefix: str) -> dict[str, int]:
    registry: dict[str, int] = {}
    used: set[int] = set()
    pending: list[str] = []

    for label in labels:
        if label is None:
            continue
        text = str(label).strip()
        if not text or text in registry:
            continue
        idx = _canonical_label_index(text, prefix)
        if idx is None or not (1 <= idx <= CTRL_VALUE_MASK) or idx in used:
            pending.append(text)
            continue
        registry[text] = idx
        used.add(idx)

    next_idx = 1
    for text in pending:
        while next_idx in used:
            next_idx += 1
        if next_idx > CTRL_VALUE_MASK:
            raise ValueError(f"too many distinct {prefix.lower()} labels for music control packing")
        registry[text] = next_idx
        used.add(next_idx)
    return registry


def _index_to_label(index: int | None, prefix: str) -> str | None:
    if index is None or index <= 0:
        return None
    return f"{prefix}{index}"


def _encode_time_step_denominator(step: float | None) -> int | None:
    if step is None:
        return None
    frac = Fraction(step).limit_denominator(CTRL_VALUE_MASK)
    if frac.numerator != 1:
        return None
    return _clamp_small(frac.denominator)


def _encode_flags(stroke: MusicStroke) -> int:
    flags = FLAG_IS_REST if stroke.is_rest else 0
    if stroke.articulations:
        for name in stroke.articulations:
            flags |= ARTICULATION_FLAGS.get(str(name), 0)
    return flags


def _decode_articulations(flags: int) -> list[str] | None:
    articulations = [name for bit, name in FLAG_TO_ARTICULATION if flags & bit]
    return articulations or None


def _emit_draw_run(words: List[int], direction: int, run_len: int) -> None:
    words.append(
        _ext_word(
            _with_subtype(
                SUBTYPE_DRAW_RUN,
                ((direction & 0x7) << 7) | (run_len & MAX_RUN),
            )
        )
    )


def pack_music_strokes(strokes: Iterable[MusicStroke], metadata=None) -> List[int]:
    if not music_enabled():
        raise RuntimeError("music packing requires STROKEGRAM_ENABLE_MUSIC=1")
    stroke_list = list(strokes)
    words: List[int] = []
    part_registry = _build_label_registry((stroke.part for stroke in stroke_list), "P")
    voice_registry = _build_label_registry((stroke.voice for stroke in stroke_list), "V")

    # Metadata header (time/key/tempo/dynamic) encoded once up front.
    words.extend(_encode_metadata(metadata))
    for stroke in stroke_list:
        anchor = _clamp_anchor(stroke.time_anchor_tick)
        part_index = part_registry.get(str(stroke.part).strip()) if stroke.part is not None else None
        voice_index = voice_registry.get(str(stroke.voice).strip()) if stroke.voice is not None else None
        flags = _encode_flags(stroke)
        program = _clamp_small(stroke.program)
        perf_onset_delta = _encode_signed_small(stroke.performance_onset_tick_delta)
        perf_duration_delta = _encode_signed_small(stroke.performance_duration_tick_delta)
        velocity = _clamp_small(stroke.velocity)
        if perf_onset_delta is not None:
            _emit_control2(words, CTRL2_TAG_PERF_ONSET_DELTA, perf_onset_delta)
        if perf_duration_delta is not None:
            _emit_control2(words, CTRL2_TAG_PERF_DURATION_DELTA, perf_duration_delta)
        if velocity is not None:
            _emit_control2(words, CTRL2_TAG_VELOCITY, velocity)
        if anchor is not None:
            _emit_control(words, CTRL_TAG_TIME_ANCHOR, anchor)
        if part_index is not None:
            _emit_control(words, CTRL_TAG_PART_INDEX, part_index)
        if voice_index is not None:
            _emit_control(words, CTRL_TAG_VOICE_INDEX, voice_index)
        if flags:
            _emit_control(words, CTRL_TAG_FLAGS, flags)
        if program is not None:
            _emit_control(words, CTRL_TAG_PROGRAM, program)

        words.append(_ext_word(_with_subtype(SUBTYPE_BOUNDARY, 1)))  # BEGIN
        commands = list(stroke.commands)
        idx = 0
        while idx < len(commands):
            cmd = commands[idx]
            if isinstance(cmd, MoveTo):
                x_val = int(cmd.x)
                y_val = int(cmd.y)
                if anchor is not None:
                    x_val -= anchor
                if not (0 <= x_val <= CANVAS_LIMIT and 0 <= y_val <= CANVAS_LIMIT):
                    raise ValueError(f"MoveTo out of range: {(cmd.x, cmd.y)}")
                words.append(_ext_word(_with_subtype(SUBTYPE_MOVE_T, x_val & CANVAS_LIMIT)))
                words.append(_ext_word(_with_subtype(SUBTYPE_MOVE_P, y_val & CANVAS_LIMIT)))
                idx += 1
            elif isinstance(cmd, DrawDir):
                dir_idx = cmd.direction & 0x7
                run_len = 1
                idx += 1
                while idx < len(commands):
                    next_cmd = commands[idx]
                    if not isinstance(next_cmd, DrawDir) or (next_cmd.direction & 0x7) != dir_idx:
                        break
                    if run_len == MAX_RUN:
                        _emit_draw_run(words, dir_idx, run_len)
                        run_len = 0
                    run_len += 1
                    idx += 1
                _emit_draw_run(words, dir_idx, run_len)
            else:
                raise TypeError(f"unknown command {cmd!r}")
        words.append(_ext_word(_with_subtype(SUBTYPE_BOUNDARY, 0)))  # END
    return words


def unpack_music_words(words: Iterable[int]) -> tuple[MusicMetadata | None, List[MusicStroke]]:
    paths: List[MusicStroke] = []
    meta = MusicMetadata()
    current_cmds: List = []
    cx = cy = 0

    pending_anchor: int | None = None
    pending_part: int | None = None
    pending_voice: int | None = None
    pending_flags = 0
    pending_program: int | None = None
    pending_perf_onset_delta: int | None = None
    pending_perf_duration_delta: int | None = None
    pending_velocity: int | None = None
    current_anchor: int | None = None
    current_part: int | None = None
    current_voice: int | None = None
    current_flags = 0
    current_program: int | None = None
    current_perf_onset_delta: int | None = None
    current_perf_duration_delta: int | None = None
    current_velocity: int | None = None

    def _flush_current() -> None:
        nonlocal current_cmds
        if current_cmds:
            pitch = None
            if current_cmds and not (current_flags & FLAG_IS_REST):
                start = current_cmds[0]
                if isinstance(start, MoveTo):
                    pitch = meta.pitch_origin + int(start.y)
            paths.append(
                MusicStroke(
                    commands=current_cmds,
                    part=_index_to_label(current_part, "P"),
                    voice=_index_to_label(current_voice, "V"),
                    pitch=pitch,
                    program=current_program,
                    is_rest=bool(current_flags & FLAG_IS_REST),
                    articulations=_decode_articulations(current_flags),
                    time_anchor_tick=current_anchor,
                    track_id=current_part,
                    performance_onset_tick_delta=current_perf_onset_delta,
                    performance_duration_tick_delta=current_perf_duration_delta,
                    velocity=current_velocity,
                )
            )
            current_cmds = []

    packed = list(words)
    idx = 0
    while idx < len(packed):
        w = packed[idx]
        mode = (w >> 18) & 0x3
        version = (w >> 16) & 0x3
        payload = w & 0xFFFF
        if mode != Mode.EXTENSION.value or not (payload & MUSIC_TYPE_BIT):
            raise ValueError(f"non-music word encountered: {w:#x}")
        if version != DEFAULT_VERSION:
            raise ValueError(f"unsupported extension version {version}")

        subtype = (payload >> SUBTYPE_SHIFT) & SUBTYPE_MASK

        if subtype == SUBTYPE_BOUNDARY:
            if payload & META_FLAG:
                meta = _decode_meta_word(payload, meta)
                idx += 1
                continue
            start = payload & 0x1
            if start == 1:
                _flush_current()
                current_anchor = pending_anchor
                current_part = pending_part
                current_voice = pending_voice
                current_flags = pending_flags
                current_program = pending_program
                current_perf_onset_delta = pending_perf_onset_delta
                current_perf_duration_delta = pending_perf_duration_delta
                current_velocity = pending_velocity
                pending_anchor = None
                pending_part = None
                pending_voice = None
                pending_flags = 0
                pending_program = None
                pending_perf_onset_delta = None
                pending_perf_duration_delta = None
                pending_velocity = None
            else:
                _flush_current()
                current_anchor = None
                current_part = None
                current_voice = None
                current_flags = 0
                current_program = None
                current_perf_onset_delta = None
                current_perf_duration_delta = None
                current_velocity = None
            idx += 1
            continue

        if subtype == SUBTYPE_MOVE_T:
            move_t_data = payload & CANVAS_LIMIT

            if idx + 1 < len(packed):
                next_w = packed[idx + 1]
                next_mode = (next_w >> 18) & 0x3
                next_version = (next_w >> 16) & 0x3
                next_payload = next_w & 0xFFFF
                if (
                    next_mode == Mode.EXTENSION.value
                    and next_version == DEFAULT_VERSION
                    and (next_payload & MUSIC_TYPE_BIT)
                    and ((next_payload >> SUBTYPE_SHIFT) & SUBTYPE_MASK) == SUBTYPE_MOVE_P
                ):
                    cy = next_payload & CANVAS_LIMIT
                    cx = move_t_data + (current_anchor or 0)
                    _flush_current()
                    current_cmds = [MoveTo(cx, cy)]
                    idx += 2
                    continue

            tag = (move_t_data >> CTRL_TAG_SHIFT) & CTRL_TAG_MASK
            value = move_t_data & CTRL_VALUE_MASK
            if tag == CTRL_TAG_TIME_ANCHOR:
                pending_anchor = value
            elif tag == CTRL_TAG_PITCH_ORIGIN:
                meta = meta.with_pitch_origin(value)
            elif tag == CTRL_TAG_TIME_STEP_DEN:
                if value <= 0:
                    raise ValueError("music time-step denominator must be > 0")
                meta = meta.with_time_step(1.0 / float(value))
            elif tag == CTRL_TAG_PART_INDEX:
                pending_part = value
            elif tag == CTRL_TAG_VOICE_INDEX:
                pending_voice = value
            elif tag == CTRL_TAG_FLAGS:
                pending_flags = value
            elif tag == CTRL_TAG_PROGRAM:
                pending_program = value
            else:
                raise ValueError(f"unknown music control tag {tag}")
            idx += 1
            continue

        if subtype == SUBTYPE_MOVE_P:
            tag = (payload >> CTRL2_TAG_SHIFT) & CTRL2_TAG_MASK
            value = payload & CTRL2_VALUE_MASK
            if tag == CTRL2_TAG_PERF_ONSET_DELTA:
                pending_perf_onset_delta = _decode_signed_small(value)
            elif tag == CTRL2_TAG_PERF_DURATION_DELTA:
                pending_perf_duration_delta = _decode_signed_small(value)
            elif tag == CTRL2_TAG_VELOCITY:
                pending_velocity = value
            else:
                raise ValueError(f"unknown music extended control tag {tag}")
            idx += 1
            continue

        if subtype == SUBTYPE_DRAW_RUN:
            dir_idx = (payload >> 7) & 0x7
            run_len = payload & MAX_RUN
            if run_len == 0:
                raise ValueError("run_len must be >=1")
            if not current_cmds:
                current_cmds.append(MoveTo(cx, cy))
            for _ in range(run_len):
                current_cmds.append(DrawDir(dir_idx))
            idx += 1
            continue

        raise ValueError(f"unknown music subtype {subtype}")

    _flush_current()
    part_programs = {}
    for stroke in paths:
        if stroke.part is None or stroke.program is None:
            continue
        part_programs.setdefault(stroke.part, int(stroke.program))
    if part_programs:
        meta = replace(meta, part_programs=part_programs)
    return meta, paths


def _encode_metadata(meta: MusicMetadata | None) -> List[int]:
    meta_words: List[int] = []
    if meta is None:
        return meta_words
    meta_template = meta if isinstance(meta, MusicMetadata) else MusicMetadata()
    pitch_origin = _clamp_small(meta_template.pitch_origin)
    if pitch_origin is not None:
        _emit_control(meta_words, CTRL_TAG_PITCH_ORIGIN, pitch_origin)
    step_denominator = _encode_time_step_denominator(meta_template.time_step_quarter)
    if step_denominator is not None:
        _emit_control(meta_words, CTRL_TAG_TIME_STEP_DEN, step_denominator)
    # Time signature (num, den) packed into 7 bits: 4+3
    if meta_template.time_signature is not None:
        num, den = meta_template.time_signature
        num_c = max(0, min(15, int(num)))
        den_c = max(0, min(7, int(den)))
        payload = (
            MUSIC_TYPE_BIT
            | (SUBTYPE_BOUNDARY << SUBTYPE_SHIFT)
            | META_FLAG
            | ((META_KIND_TIMESIG & META_KIND_MASK) << META_KIND_SHIFT)
            | (((num_c << 3) | (den_c & 0x7)) & META_VALUE_MASK)
        )
        meta_words.append(_ext_word(payload))
    # Key signature
    if meta_template.key_signature is not None:
        key_c = max(0, min(META_VALUE_MASK, meta_template.key_signature + 64))
        payload = (
            MUSIC_TYPE_BIT
            | (SUBTYPE_BOUNDARY << SUBTYPE_SHIFT)
            | META_FLAG
            | ((META_KIND_KEY & META_KIND_MASK) << META_KIND_SHIFT)
            | key_c
        )
        meta_words.append(_ext_word(payload))
    # Tempo (store bpm)
    if meta_template.tempo is not None:
        tempo_c = max(0, min(META_VALUE_MASK, int(round(meta_template.tempo))))
        payload = (
            MUSIC_TYPE_BIT
            | (SUBTYPE_BOUNDARY << SUBTYPE_SHIFT)
            | META_FLAG
            | ((META_KIND_TEMPO & META_KIND_MASK) << META_KIND_SHIFT)
            | tempo_c
        )
        meta_words.append(_ext_word(payload))
    # Dynamic (best-effort code)
    dyn_code = getattr(meta_template, "dynamic_base", None)
    if dyn_code:
        payload = (
            MUSIC_TYPE_BIT
            | (SUBTYPE_BOUNDARY << SUBTYPE_SHIFT)
            | META_FLAG
            | ((META_KIND_DYNAMIC & META_KIND_MASK) << META_KIND_SHIFT)
            | (dyn_code & META_VALUE_MASK)
        )
        meta_words.append(_ext_word(payload))
    return meta_words


def _decode_meta_word(payload: int, meta: MusicMetadata) -> MusicMetadata:
    kind = (payload >> META_KIND_SHIFT) & META_KIND_MASK
    value = payload & META_VALUE_MASK
    if kind == META_KIND_TIMESIG:
        num = (value >> 3) & 0xF
        den = value & 0x7
        if num and den:
            meta = meta.with_time_signature((num, den))
    elif kind == META_KIND_KEY:
        key = int(value) - 64
        meta = meta.with_key_signature(key)
    elif kind == META_KIND_TEMPO:
        tempo_bpm = value
        meta = meta.with_tempo(float(tempo_bpm))
    elif kind == META_KIND_DYNAMIC:
        code = value
        meta = replace(meta, dynamic_base=code)
    return meta
