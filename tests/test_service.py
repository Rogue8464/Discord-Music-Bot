import pytest
import discord
from unittest.mock import AsyncMock, MagicMock
from src.service import MusicService
from src.models.domain import Song

# 告訴 pytest 這個檔案裡面有 async 測試
pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_dependencies():
    """使用 fixture 準備假的相依物件"""
    bot = MagicMock()
    queue = MagicMock()
    extractor = AsyncMock() # 因為 extract_info 已經改成 async，所以用 AsyncMock
    return bot, queue, extractor

async def test_join_channel_success(mock_dependencies):
    bot, queue, extractor = mock_dependencies
    service = MusicService(bot, queue, extractor)

    # 偽造 Discord 的 Context (TextChannel 與 Member)
    mock_channel = AsyncMock(spec=discord.TextChannel)
    mock_author = MagicMock(spec=discord.Member)
    
    # 模擬使用者在語音頻道內
    mock_author.voice.channel = AsyncMock()
    # 模擬機器人尚未加入語音頻道
    mock_author.guild.voice_client = None 

    # 執行測試
    result = await service.join_channel(mock_channel, mock_author)

    # 驗證：是否回傳 True？是否成功呼叫了 voice_channel.connect()？
    assert result is True
    mock_author.voice.channel.connect.assert_called_once()

async def test_join_channel_fail_when_user_not_in_voice(mock_dependencies):
    bot, queue, extractor = mock_dependencies
    service = MusicService(bot, queue, extractor)

    mock_channel = AsyncMock(spec=discord.TextChannel)
    mock_author = MagicMock(spec=discord.Member)
    
    # 模擬使用者「不在」語音頻道內
    mock_author.voice = None

    result = await service.join_channel(mock_channel, mock_author)

    # 驗證：是否攔截成功回傳 False？是否發送了警告訊息？
    assert result is False
    mock_channel.send.assert_called_once_with("你需要先加入一個語音頻道！")

async def test_skip_music_success(mock_dependencies):
    bot, queue, extractor = mock_dependencies
    service = MusicService(bot, queue, extractor)

    mock_guild = MagicMock(spec=discord.Guild)
    # 模擬有語音連線，且正在播放音樂
    mock_guild.voice_client = MagicMock()
    mock_guild.voice_client.is_playing.return_value = True

    result = await service.skip(mock_guild)

    # 驗證：是否回傳 True？是否呼叫了 stop() 切歌？
    assert result is True
    mock_guild.voice_client.stop.assert_called_once()