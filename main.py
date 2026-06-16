import os
import aiohttp
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
# 模組
from src.models.interfaces import IVideoSearcher, IAudioPlayer
from src.models.domain import InMemoryQueue
from src.models.extractors import YTDLPExtractor
from src.service import MusicService
from src.crawl import YouTubeCrawler
from src.ui import YouTubeSearchView

load_dotenv()
BOT_TOKEN = os.getenv("TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

class MusicBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=discord.Intents.all())

    async def setup_hook(self):
        if GUILD_ID:
            try:
                # 如果有填寫 GUILD_ID，執行秒級的特定伺服器同步
                guild = discord.Object(id=int(GUILD_ID))
                self.tree.copy_global_to(guild=guild)
                await self.tree.sync(guild=guild)
                print(f"✅ 斜線指令已秒級同步至特定伺服器 (ID: {GUILD_ID})")
            except Exception as e:
                print(f"❌ 同步至特定伺服器失敗: {e}")
        else:
            # 如果沒有填寫，則執行全域同步 (需較長時間生效)
            await self.tree.sync()
            print("⚠️ 未設定 GUILD_ID，已執行全域指令同步 (這可能需要最多一小時才會在各伺服器生效)")

bot = MusicBot()

# 依賴注入 (Dependency Injection) 的準備
# 將具體的實作 (InMemoryQueue, YTDLPExtractor) 綁定起來
music_queue = InMemoryQueue()
audio_extractor = YTDLPExtractor()

# 初始化 Service，將介面實作注入其中
music_service = MusicService(bot, music_queue, audio_extractor)

# 系統組裝
video_searcher: IVideoSearcher = YouTubeCrawler()
# 將 MusicService 向上轉型視為 IAudioPlayer
music_player: IAudioPlayer = MusicService(bot, music_queue, audio_extractor)



@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_command_error(ctx, error):
    """全域錯誤捕捉器，防止指令異常導致程式崩潰"""
    
    # 判斷是否為指令執行過程中引發的錯誤
    if isinstance(error, commands.CommandInvokeError):
        original_error = error.original
        
        # 攔截 aiohttp 的 ClientConnectorError，並檢查是否包含 10013 錯誤碼
        if isinstance(original_error, aiohttp.ClientConnectorError) and "10013" in str(original_error):
            await ctx.send("⚠️ 網路連線瞬間被作業系統阻擋，請稍後再試一次！")
            print(f"[網路波動攔截] WinError 10013 阻斷: {original_error}")
            return
            
    # 如果使用者輸入了不存在的指令 (例如 !xyz)，我們直接忽略，不要在終端機報錯
    if isinstance(error, commands.CommandNotFound):
        return

    # 若是其他未預期的錯誤，正常印出以便未來除錯
    print(f"[未處理錯誤] 執行 {ctx.command} 時發生錯誤: {error}")

# ================= 斜線指令定義區塊 =================

@bot.tree.command(name="join", description="讓機器人加入您所在的語音頻道")
async def join(interaction: discord.Interaction):
    # 斜線指令的起手式：延遲回應，爭取運算時間
    await interaction.response.defer()
    
    # 從 interaction 提取 channel 與 user
    success = await music_player.join_channel(interaction.channel, interaction.user)
    if success:
        await interaction.followup.send("✅ 已成功加入語音頻道！")
    else:
        # 如果 Service 內部已經發送過錯誤訊息，這裡可以選擇刪除或略過
        pass

@bot.tree.command(name="play", description="直接播放 YouTube 音樂連結")
@app_commands.describe(url="YouTube 影片或音樂的網址")
async def play(interaction: discord.Interaction, url: str):
    # 1. 延遲回應並設為隱藏 (僅發送者可見)
    await interaction.response.defer(ephemeral=True)
    
    # 2. Service 內部會自行向 interaction.channel 發送「公開」的正在播放訊息
    await music_player.play_url(interaction.channel, interaction.user, url)
    
    # 3. 給使用者的「私密」確認回饋
    await interaction.followup.send("🎵 播放請求已處理完成。", ephemeral=True)

@bot.tree.command(name="skip", description="跳過當前播放的歌曲")
async def skip(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    success = await music_player.skip(interaction.guild)
    
    if success:
        # 公開廣播讓頻道所有人知道
        await interaction.channel.send(f"⏭️ **{interaction.user.display_name}** 跳過了當前歌曲。")
        # 私密確認
        await interaction.followup.send("✅ 指令執行成功。", ephemeral=True)
    else:
        await interaction.followup.send("⚠️ 目前沒有正在播放的歌曲。", ephemeral=True)

@bot.tree.command(name="stop", description="停止播放並清空隊列")
async def stop(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    success = await music_player.stop(interaction.guild)
    
    if success:
        await interaction.channel.send(f"🛑 **{interaction.user.display_name}** 已清空隊列並讓機器人離開頻道。")
        await interaction.followup.send("✅ 指令執行成功。", ephemeral=True)
    else:
        await interaction.followup.send("⚠️ 機器人目前不在語音頻道中。", ephemeral=True)

@bot.tree.command(name="pause", description="暫停當前播放的音樂")
async def pause(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    success = await music_player.pause(interaction.guild)
    
    if success:
        await interaction.channel.send(f"⏸️ **{interaction.user.display_name}** 暫停了音樂。")
        await interaction.followup.send("✅ 指令執行成功。", ephemeral=True)
    else:
        await interaction.followup.send("⚠️ 目前沒有正在播放的音樂，無法暫停。", ephemeral=True)

@bot.tree.command(name="resume", description="繼續播放暫停的音樂")
async def resume(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    success = await music_player.resume(interaction.guild)
    
    if success:
        await interaction.channel.send(f"▶️ **{interaction.user.display_name}** 繼續了音樂播放。")
        await interaction.followup.send("✅ 指令執行成功。", ephemeral=True)
    else:
        await interaction.followup.send("⚠️ 目前沒有被暫停的音樂。", ephemeral=True)

# --- 要求設定為僅發送者可見 (Ephemeral) 的指令 ---
@bot.tree.command(name="queue", description="顯示目前的播放隊列 (僅自己可見)")
async def queue(interaction: discord.Interaction):
    # 設定 ephemeral=True 讓這則訊息只有呼叫指令的人看得到
    msg = ""
    if music_queue.current_song:
        msg += f"**▶️ 當前正在播放:**\n {music_queue.current_song.title}\n\n"
    
    songs = music_queue.all_songs
    if songs:
        queue_str = "\n".join([f"{i+1}. {song.title}" for i, song in enumerate(songs)])
        msg += f"**📜 接下來的歌曲:**\n{queue_str}"
    
    # 這裡可以直接 send_message，因為讀取記憶體很快，不需要 defer
    await interaction.response.send_message(msg if msg else "隊列是空的。", ephemeral=True)

@bot.tree.command(name="search", description="透過關鍵字搜尋 YouTube 影片 (僅自己可見)")
@app_commands.describe(keyword="想搜尋的歌曲或影片名稱")
async def search(interaction: discord.Interaction, keyword: str):
    # 搜尋可能需要幾秒鐘，使用 defer(ephemeral=True) 確保之後的 followup 也是隱藏的
    await interaction.response.defer(ephemeral=True)
    
    song_names, song_urls = await video_searcher.search_videos(keyword)
    
    if not song_names:
        await interaction.followup.send("❌ 查無結果，請嘗試其他關鍵字。", ephemeral=True)
        return
    
    view = YouTubeSearchView(
        player=music_player, 
        text_channel=interaction.channel, 
        author=interaction.user, 
        song_names=song_names, 
        song_urls=song_urls
    )
    
    # 使用 followup 傳送包含按鈕的隱藏訊息
    await interaction.followup.send(content=view.get_content(), view=view, ephemeral=True)

bot.run(BOT_TOKEN)