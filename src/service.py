import discord
from discord.ext import commands
import asyncio
from src.models.interfaces import IAudioExtractor, IMusicQueue, IAudioPlayer
from src.models.domain import Song

class MusicService(IAudioPlayer):
    def __init__(self, bot: commands.Bot, queue: IMusicQueue, extractor: IAudioExtractor):
        self.bot = bot
        self.queue = queue
        self.extractor = extractor
        self.ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -fflags +genpts -fflags nobuffer -vn',
            'options': '-vn -b:a 320k -loglevel panic'
        }

    async def join_channel(self, text_channel: discord.TextChannel, author: discord.Member) -> bool:
        if author.voice is None:
            await text_channel.send("你需要先加入一個語音頻道！")
            return False
        
        voice_channel = author.voice.channel
        guild = author.guild
        
        if guild.voice_client is not None:
            await guild.voice_client.move_to(voice_channel)
        else:
            await voice_channel.connect()
        return True

    async def play_url(self, text_channel: discord.TextChannel, author: discord.Member, url: str) -> None:
        guild = author.guild
        if guild.voice_client is None and not await self.join_channel(text_channel, author):
            return

        song = await self.extractor.extract_info(url)
        if not song:
            await text_channel.send("無法解析該網址。")
            return

        voice_client = guild.voice_client
        if voice_client.is_playing() or voice_client.is_paused():
            self.queue.enqueue(song)
            await text_channel.send(f'已將 {song.title} 加入播放隊列')
        else:
            await self._play_song(text_channel, voice_client, song)

    async def _play_song(self, text_channel: discord.TextChannel, voice_client: discord.VoiceClient, song: Song):
        if not song.stream_url:
            await text_channel.send("未能找到有效的音頻流。")
            return

        self.queue.current_song = song
        source = discord.FFmpegPCMAudio(song.stream_url, **self.ffmpeg_options)

        def after_playing(error):
            if error: print(f"播放錯誤: {error}")
            coro = self._play_next(text_channel, voice_client)
            asyncio.run_coroutine_threadsafe(coro, self.bot.loop)

        voice_client.play(source, after=after_playing)
        await text_channel.send(f'正在播放: {song.title}')

    async def _play_next(self, text_channel: discord.TextChannel, voice_client: discord.VoiceClient):
        next_song = self.queue.dequeue()
        if next_song:
            refreshed_song = await self.extractor.extract_info(next_song.url)
            if refreshed_song:
                await self._play_song(text_channel, voice_client, refreshed_song)
            else:
                # 如果這首歌突然無法解析，自動跳下一首
                await text_channel.send(f"無法取得 **{next_song.title}** 的音訊，自動跳過。")
                await self._play_next(text_channel, voice_client)
        else:
            self.queue.current_song = None
            await text_channel.send("隊列中的所有歌曲已播放完畢！")

    async def skip(self, guild: discord.Guild) -> bool:
        if guild.voice_client and guild.voice_client.is_playing():
            guild.voice_client.stop() # 這會自動觸發 _play_next
            return True
        return False

    async def stop(self, guild: discord.Guild) -> bool:
        if guild.voice_client:
            self.queue.clear() # 清空隊列
            guild.voice_client.stop()
            await guild.voice_client.disconnect()
            return True
        return False
    
    async def pause(self, guild: discord.Guild) -> bool:
        """實作暫停邏輯"""
        if guild.voice_client and guild.voice_client.is_playing():
            guild.voice_client.pause()
            return True
        return False

    async def resume(self, guild: discord.Guild) -> bool:
        """實作繼續播放邏輯"""
        if guild.voice_client and guild.voice_client.is_paused():
            guild.voice_client.resume()
            return True
        return False