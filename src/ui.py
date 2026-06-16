import discord
from src.models.interfaces import IAudioPlayer

SONGS_PER_PAGE = 5
TIMEOUT = 120

class YouTubeSearchView(discord.ui.View):
    """處理 YouTube 搜尋結果的分頁與互動按鈕"""

    def __init__(self, player: IAudioPlayer, text_channel: discord.TextChannel, author: discord.Member, song_names: list, song_urls: list):
        super().__init__(timeout=TIMEOUT)
        self.player = player  # 重新命名變數，語意更符合其介面職責
        self.text_channel = text_channel
        self.author = author
        self.song_names = song_names
        self.song_urls = song_urls
        self.page = 0
        self.update_buttons_state()

    def get_content(self) -> str:
        """根據當前頁數產生訊息內容"""
        start = self.page * SONGS_PER_PAGE
        end = min(start + SONGS_PER_PAGE, len(self.song_names))
        msg = ""
        emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']
        
        for i in range(start, end):
            msg += f"{emojis[i-start]} {self.song_names[i]}\n<{self.song_urls[i]}>\n"
        msg += f"\n顯示第 {start+1}~{end} 筆結果，共 {len(self.song_names)} 筆結果"
        return msg

    def update_buttons_state(self):
        """根據當前頁數，動態啟用或禁用按鈕"""
        start = self.page * SONGS_PER_PAGE
        end = min(start + SONGS_PER_PAGE, len(self.song_names))
        count = end - start
        
        # 動態控制數字按鈕是否可用
        self.btn_1.disabled = count < 1
        self.btn_2.disabled = count < 2
        self.btn_3.disabled = count < 3
        self.btn_4.disabled = count < 4
        self.btn_5.disabled = count < 5
        
        # 控制翻頁按鈕
        self.btn_prev.disabled = self.page == 0
        self.btn_next.disabled = end >= len(self.song_names)

    async def handle_selection(self, interaction: discord.Interaction, index: int):
        # 在斜線指令的隱藏訊息中，通常不需要檢查 user != self.author
        # 因為別人根本看不到這則訊息，也按不到按鈕，但保留作為雙重防護也無妨
        if interaction.user != self.author:
            await interaction.response.send_message("你不能操作別人的搜尋選單！", ephemeral=True)
            return
        
        target_idx = self.page * 5 + index
        url = self.song_urls[target_idx]
        title = self.song_names[target_idx]
        
        self.stop()
        
        # 編輯原有的隱藏訊息，顯示選擇結果，並移除按鈕 (view=None)
        await interaction.response.edit_message(content=f"✅ 已為您選擇並處理: **{title}**", view=None)
        
        # 呼叫 Service 播放，Service 內部的訊息會公開發送到該頻道
        await self.player.play_url(self.text_channel, interaction.user, url)

    # ================= UI 元件定義 =================

    @discord.ui.button(emoji="◀", style=discord.ButtonStyle.primary, row=0)
    async def btn_prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page -= 1
        self.update_buttons_state()
        await interaction.response.edit_message(content=self.get_content(), view=self)

    @discord.ui.button(emoji="1️⃣", style=discord.ButtonStyle.secondary, row=1)
    async def btn_1(self, interaction, button): await self.handle_selection(interaction, 0)

    @discord.ui.button(emoji="2️⃣", style=discord.ButtonStyle.secondary, row=1)
    async def btn_2(self, interaction, button): await self.handle_selection(interaction, 1)

    @discord.ui.button(emoji="3️⃣", style=discord.ButtonStyle.secondary, row=1)
    async def btn_3(self, interaction, button): await self.handle_selection(interaction, 2)

    @discord.ui.button(emoji="4️⃣", style=discord.ButtonStyle.secondary, row=1)
    async def btn_4(self, interaction, button): await self.handle_selection(interaction, 3)

    @discord.ui.button(emoji="5️⃣", style=discord.ButtonStyle.secondary, row=1)
    async def btn_5(self, interaction, button): await self.handle_selection(interaction, 4)

    @discord.ui.button(emoji="▶", style=discord.ButtonStyle.primary, row=0)
    async def btn_next(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page += 1
        self.update_buttons_state()
        await interaction.response.edit_message(content=self.get_content(), view=self)