# 🎵 Discord Music Bot

🌐 **Language / 語言:** [繁體中文](README.md) | [English](README_EN.md)

A modern Discord music bot built with `discord.py`.  
This project is refactored with **SOLID principles** and **Clean Architecture**, featuring high cohesion and low coupling. It supports asynchronous processing, multithreaded audio resolution, and Discord's latest **Slash Commands** with interactive UI views.

## ✨ Key Features

* **Modern Interaction**: Full support for `/command` slash commands with ephemeral responses to keep channels clean.
* **Interactive Search**: Uses Selenium for background scraping, providing `/search` keyword search with paginated UI buttons.
* **Smooth Playback**: Offloads `yt-dlp` extraction to background threads via `asyncio.to_thread`, eliminating voice stutter and packet drops during resolution.
* **Dependency Inversion**: Business logic (`Service`) is decoupled from external frameworks, making it easy to test and extend.

---

## 🛠️ Prerequisites

Before running the bot, make sure the following core components are installed on your system:

1. **Python 3.10+** (Python 3.13 recommended) or **`uv`**
2. **FFmpeg**: Core engine for audio processing and streaming.
   * Verify installation: Run `ffmpeg -version` in your terminal; seeing version info confirms it is installed and in your `PATH`.
3. **Google Chrome**: Used by Selenium to scrape YouTube search results.

---

## 🚀 Installation & Setup

### Option A: Windows One-Click Launcher (`run.bat`, Recommended)

On Windows, you can simply double-click `run.bat` (or run `.\run.bat` in a terminal). The script automatically performs the following checks and setup:

1. **FFmpeg Check**: Verifies `ffmpeg` is available in your system `PATH`.
2. **`.env` Check**: If `.env` does not exist, it copies `.env.example` to `.env` and prompts you to fill in your `TOKEN`.
3. **Environment & `.venv` Setup**: Automatically detects `uv` (preferred) or `python` / `py -3`, creates `.venv` if missing, and installs dependencies from `requirements.txt` (or repairs missing packages).
4. **Launch**: Starts `main.py` using `.venv\Scripts\python.exe`.

### Option B: Manual Installation

#### 1. Clone the repository & install dependencies

You can use either standard `pip` or the modern package manager `uv`:

**Using standard `pip`:**
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

**Using `uv` (recommended, faster):**
```bash
# Create virtual environment and install dependencies
uv venv
uv pip install -r requirements.txt
```

If you encounter `yt_dlp` errors when running the bot, update it with `pip install --upgrade yt-dlp` or `uv pip install --upgrade yt-dlp`.

#### 2. Environment Variables (`.env`)

Find `.env.example` in the project root, copy it to `.env`, and fill in the following fields:

```bash
# Your Discord Bot Token (Required)
# Get it from Discord Developer Portal > Bot > Reset Token
TOKEN=your_bot_token

# Your Discord Guild/Server ID (Optional)
# Enables instant slash command sync for that guild. Without it, global sync can take up to 1 hour.
GUILD_ID=# Enter numeric ID, or leave blank / remove this line
```

---

## 🎮 Usage

Once everything is configured, start the bot:

* **Windows**: Double-click `run.bat` (or run `.\run.bat`)
* **Manual**:
  ```bash
  python .\main.py
  ```
  (or `uv run .\main.py`)

When the terminal prints `Logged in as [Your Bot Name]` and `斜線指令已同步完成！`, type `/` in Discord to use the following commands:

| Command | Description | Message Visibility |
|-----|-----|-----|
| `/join` | Join your current voice channel | Public |
| `/play <url>` | Play a YouTube video or music URL | Ephemeral feedback / Public playback status |
| `/search <keyword>` | Search YouTube by keyword with paginated selection buttons | Ephemeral (sender only, including results) |
| `/queue` | Display the current playback queue and now playing track | Ephemeral (sender only) |
| `/skip` | Skip the currently playing track | Ephemeral feedback / Public skip status |
| `/pause` | Pause the currently playing track | Ephemeral feedback / Public pause status |
| `/resume` | Resume a paused track | Ephemeral feedback / Public playback status |
| `/stop` | Stop playback, clear the queue, and leave the voice channel | Ephemeral feedback / Public leave status |

---

## 🧪 Running Tests

This project includes unit tests using `pytest` and `pytest-asyncio`.  
Make sure `pytest.ini` exists in the project root with `pythonpath = .`.

Run all tests:
```bash
pytest -v
```
(or `uv run pytest -v`)
