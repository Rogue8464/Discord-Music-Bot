from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class Song:
    url: str
    title: str
    stream_url: Optional[str] = None
    info: Optional[Dict] = None

class InMemoryQueue:
    """實作佇列邏輯 (這不需要依賴介面，它是單純的資料容器)"""
    def __init__(self):
        self._queue = []
        self.current_song: Optional[Song] = None

    def enqueue(self, song: Song):
        self._queue.append(song)

    def dequeue(self) -> Optional[Song]:
        return self._queue.pop(0) if self._queue else None

    def clear(self):
        self._queue.clear()
        self.current_song = None

    @property
    def is_empty(self) -> bool:
        return len(self._queue) == 0

    @property
    def all_songs(self):
        return self._queue.copy()