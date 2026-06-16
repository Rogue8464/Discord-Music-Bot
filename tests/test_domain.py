import pytest
from src.models.domain import Song, InMemoryQueue

def test_queue_enqueue_and_dequeue():
    # 準備階段 (Arrange)
    queue = InMemoryQueue()
    song1 = Song(url="http://test1", title="Song 1")
    song2 = Song(url="http://test2", title="Song 2")

    # 執行階段 (Act)
    queue.enqueue(song1)
    queue.enqueue(song2)

    # 驗證階段 (Assert)
    assert queue.is_empty is False
    assert len(queue.all_songs) == 2
    
    # 測試出隊邏輯
    popped_song = queue.dequeue()
    assert popped_song.title == "Song 1"
    assert len(queue.all_songs) == 1

def test_queue_clear():
    queue = InMemoryQueue()
    queue.enqueue(Song(url="http://test", title="Test"))
    queue.current_song = Song(url="http://playing", title="Playing")
    
    queue.clear()
    
    assert queue.is_empty is True
    assert queue.current_song is None