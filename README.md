# 🎵 Discord Music Bot

這是一個基於 `discord.py` 開發的現代化 Discord 音樂機器人。
本專案採用 **SOLID 原則** 與 **整潔架構 (Clean Architecture)** 進行重構，具備高內聚、低耦合的特性。支援非同步 (Async) 處理、多執行緒 (Multithreading) 音訊解析，並全面採用 Discord 最新的**斜線指令 (Slash Commands)** 與 UI 視圖互動。

## ✨ 核心特色

* **現代化互動**：全面支援 `/command` 斜線指令，並使用隱藏訊息 (Ephemeral) 確保頻道版面整潔。
* **互動式搜尋**：使用 Selenium 進行背景爬蟲，提供 `/search` 關鍵字搜尋與 UI 按鈕翻頁功能。
* **流暢播放**：利用 `asyncio.to_thread` 將 `yt-dlp` 解析任務移至背景執行，徹底解決解析時造成的語音卡頓與掉包問題。
* **依賴反轉設計**：業務邏輯層 (Service) 與外部框架完全解耦，易於測試與擴充。

---

## 🛠️ 環境需求 (Prerequisites)

在開始執行機器人之前，請確保您的系統已安裝以下核心組件：

1.  **Python 3.10+** (推薦使用最新的 Python 3.13)
2.  **FFmpeg**：機器人處理與串流音訊的核心引擎。
    * 驗證安裝：在終端機輸入 `ffmpeg -version`，若有顯示版本號即代表安裝成功。
3.  **Google Chrome 瀏覽器**：供 Selenium 爬蟲抓取 YouTube 搜尋結果使用。

---

## 🚀 安裝與設定 (Installation & Setup)

### 1. 取得程式碼與安裝依賴

首先，將專案下載到本機，並安裝所需的 Python 套件。這裡提供標準 `pip` 與現代套件管理器 `uv` 兩種方式：

**使用標準 `pip`:**
```bash
# 建立虛擬環境
python -m venv .venv

# 啟動虛擬環境 (Windows)
.venv\Scripts\activate

# 更新並安裝 requirements
pip install -r requirements.txt
```

使用 uv (推薦，速度更快):
```bash
# 建立並同步虛擬環境依賴
uv venv
uv pip install -r requirements.txt
```
若執行程式時遇到 `yt_dlp` 出錯則執行 `pip install --upgrade yt-dlp` 或 `uv pip install --upgrade yt-dlp` 更新套件即可

### 2. 環境變數設定 (.env)
在專案的根目錄下找到一個名為 `.env.example` 的檔案，並填入以下資訊：

```bash
# 你的 Discord 機器人 Token (必填)
# 可至 Discord Developer Portal > Bot > Reset Token 取得
TOKEN=你的機器人Token

# 你的 Discord 伺服器 ID (選填)
# 填寫此欄位可達成斜線指令的「秒級同步」。若不填，指令可能需要最高一小時才能在全域生效。
GUILD_ID=# 填入數字即可，若不填請留空或刪除此行
```
填完後將其重命名為 `.env`

---
## 🎮 實際使用 (Usage)
確認所有設定就緒後，啟動機器人：
```bash
python .\main.py
```
(或者使用 `uv run .\main.py`)

當終端機顯示 `Logged in as [你的機器人名稱]` 與 `斜線指令已同步完成！` 時，即可在 Discord 中輸入 `/` 開始使用以下指令：

| 指令 | 說明 | 訊息可見度 |
|-----|-----|-----|
| `/join` | 讓機器人加入您目前所在的語音頻道| 公開 |
| `/play <url>` | 直接播放 YouTube 影片或音樂網址| 指令回饋隱藏 / 播放狀態公開 |
| `/yt <keyword>` | 透過關鍵字搜尋 YouTube，並提供按鈕翻頁選歌 | 僅發送者可見 (包含搜尋清單) |
| `/queue` | 顯示目前的播放隊列與正在播放的歌曲 | 僅發送者可見 |
| `/skip` | 跳過當前正在播放的歌曲 | 指令回饋隱藏 / 切歌狀態公開
| `/pause` | 暫停當前播放的音樂 | 指令回饋隱藏 / 暫停狀態公開
| `/resume` | 繼續播放被暫停的音樂 | 指令回饋隱藏 / 播放狀態公開 |
| `/stop` | 停止播放、清空所有隊列並離開語音頻道 | 指令回饋隱藏 / 離開狀態公開 
---
## 🧪 執行單元測試 (Running Tests)
本專案具備完善的單元測試，使用 `pytest` 與 `pytest-asyncio` 進行邏輯驗證。
執行測試前，請確保根目錄下有 `pytest.ini` 檔案配置了 `pythonpath = .`。

執行所有測試：
```bash
pytest -v
```
(或 `uv run pytest -v`)