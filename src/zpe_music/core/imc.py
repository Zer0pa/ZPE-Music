from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Sequence, Tuple

from .constants import WORD_MASK
from ..music.grid import events_to_grid
from ..music.pack import MUSIC_TYPE_BIT, pack_music_strokes, unpack_music_words
from ..music.parser import musicxml_to_events
from ..music.strokes import grid_to_strokes
from ..music.types import MusicMetadata, MusicStroke


@dataclass
class IMCResult:
    text: str = ""
    music_blocks: List[Tuple[MusicMetadata | None, List[MusicStroke]]] = field(default_factory=list)
    word_count: int = 0


class IMCEncoder:
    """Minimal music-only IMC surface for the standalone public repo."""

    def __init__(self) -> None:
        self._stream: List[int] = []

    def add_music(self, musicxml_path: str | Path) -> "IMCEncoder":
        metadata, events = musicxml_to_events(str(musicxml_path))
        grid = events_to_grid(events, metadata)
        words = pack_music_strokes(grid_to_strokes(grid), metadata=grid.metadata)
        for word in words:
            if not isinstance(word, int):
                raise TypeError(f"music encoder produced non-int word: {word!r}")
            if word < 0 or word > WORD_MASK:
                raise ValueError(f"music encoder produced out-of-range word: {word}")
            if not (word & 0xFFFF & MUSIC_TYPE_BIT):
                raise ValueError(f"music word missing music type bit: {word:#x}")
        self._stream.extend(words)
        return self

    def build(self) -> List[int]:
        return list(self._stream)


class IMCDecoder:
    """Minimal music-only decoder for the standalone public repo."""

    def decode(self, stream: Sequence[int]) -> IMCResult:
        packed = list(stream)
        music_blocks = [unpack_music_words(packed)] if packed else []
        return IMCResult(music_blocks=music_blocks, word_count=len(packed))
