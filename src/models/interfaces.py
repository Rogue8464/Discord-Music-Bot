from abc import ABC, abstractmethod
from typing import Optional, Tuple, List
from .domain import Song
import discord

class IAudioExtractor(ABC):
    """音訊解析與搜尋的抽象介面"""
    @abstractmethod
    async def extract_info(self, url: str) -> Optional[Song]:
        """負責解析網址並回傳歌曲資訊"""
        pass

class IVideoSearcher(ABC):
    """專職處理關鍵字搜尋的抽象介面"""
    @abstractmethod
    async def search_videos(self, keyword: str) -> Tuple[List[str], List[str]]:
        """回傳 (歌名列表, 網址列表)"""
        pass

class IAudioPlayer(ABC):
    """
    定義播放音樂的抽象介面。
    讓 UI 視圖層只依賴這個介面，而不依賴具體的 Service。
    """
    @abstractmethod
    async def play_url(self, text_channel: discord.TextChannel, author: discord.Member, url: str) -> None:
        pass

    @abstractmethod
    async def skip(self, guild: discord.Guild) -> bool:
        """跳過當前歌曲，回傳是否成功執行"""
        pass

    @abstractmethod
    async def stop(self, guild: discord.Guild) -> bool:
        """停止播放並清空隊列，回傳是否成功執行"""
        pass
    
    @abstractmethod
    async def pause(self, guild: discord.Guild) -> bool:
        """暫停當前播放的音樂，回傳是否成功執行"""
        pass

    @abstractmethod
    async def resume(self, guild: discord.Guild) -> bool:
        """繼續播放已暫停的音樂，回傳是否成功執行"""
        pass

class IMusicQueue(ABC):
    """播放佇列的抽象介面"""
    @abstractmethod
    def enqueue(self, song: Song) -> None:
        pass
    
    @abstractmethod
    def dequeue(self) -> Optional[Song]:
        pass
    
    @abstractmethod
    def clear(self) -> None:
        pass
    
    @property
    @abstractmethod
    def is_empty(self) -> bool:
        pass
    
    @property
    @abstractmethod
    def all_songs(self) -> List[Song]:
        pass