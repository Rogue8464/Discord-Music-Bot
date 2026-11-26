@echo off
chcp 65001 >nul 2>&1
setlocal EnableDelayedExpansion

cd /d "%~dp0"
title Discord Music Bot

echo ==================================================
echo   Discord Music Bot - Environment Check ^& Launch
echo ==================================================
echo.

:: 1. Check FFmpeg
echo [1/4] Checking FFmpeg...
where ffmpeg >nul 2>&1
if errorlevel 1 (
    echo [ERROR] FFmpeg was not found in PATH.
    echo Please install FFmpeg and add it to your system PATH.
    echo Download: https://ffmpeg.org/download.html
    goto :fail
)
echo [OK] FFmpeg found.
echo.

:: 2. Check .env configuration
echo [2/4] Checking .env configuration...
if not exist ".env" (
    if exist ".env.example" (
        copy /Y ".env.example" ".env" >nul
        echo [WARN] .env not found. Created .env from .env.example.
        echo Please edit .env and fill in your Discord bot TOKEN, then run this script again.
    ) else (
        echo [ERROR] .env file not found. Please create .env with your Discord bot TOKEN.
    )
    goto :fail
)
echo [OK] .env found.
echo.

:: 3. Detect uv or Python and set up .venv
echo [3/4] Checking Python / uv and virtual environment...
set "USE_UV=0"
set "PY_CMD="

where uv >nul 2>&1
if not errorlevel 1 (
    set "USE_UV=1"
    echo [OK] uv detected.
) else (
    python --version >nul 2>&1
    if not errorlevel 1 (
        set "PY_CMD=python"
        echo [OK] Python detected ^(^python^).
    ) else (
        py -3 --version >nul 2>&1
        if not errorlevel 1 (
            set "PY_CMD=py -3"
            echo [OK] Python detected ^(^py -3^).
        ) else (
            echo [ERROR] Neither uv nor Python 3 was found.
            echo Please install Python 3.10+ ^(https://www.python.org/^) or uv ^(https://docs.astral.sh/uv/^).
            goto :fail
        )
    )
)

if not exist ".venv\Scripts\python.exe" (
    echo [INFO] Virtual environment ^(.venv^) not found. Creating...
    if "!USE_UV!"=="1" (
        uv venv .venv
        if errorlevel 1 (
            echo [ERROR] Failed to create virtual environment with uv.
            goto :fail
        )
        if exist "requirements.txt" (
            echo [INFO] Installing dependencies with uv...
            uv pip install -r requirements.txt
            if errorlevel 1 (
                echo [ERROR] Failed to install dependencies with uv.
                goto :fail
            )
        )
    ) else (
        !PY_CMD! -m venv .venv
        if errorlevel 1 (
            echo [ERROR] Failed to create virtual environment with !PY_CMD!.
            goto :fail
        )
        ".venv\Scripts\python.exe" -m pip install --upgrade pip
        if exist "requirements.txt" (
            echo [INFO] Installing dependencies with pip...
            ".venv\Scripts\python.exe" -m pip install -r requirements.txt
            if errorlevel 1 (
                echo [ERROR] Failed to install dependencies with pip.
                goto :fail
            )
        )
    )
    echo [OK] Virtual environment created and dependencies installed.
) else (
    echo [OK] Virtual environment ^(.venv^) found.
    ".venv\Scripts\python.exe" -c "import discord" >nul 2>&1
    if errorlevel 1 (
        echo [WARN] Missing dependencies in .venv. Installing from requirements.txt...
        if exist "requirements.txt" (
            if "!USE_UV!"=="1" (
                uv pip install -r requirements.txt
            ) else (
                ".venv\Scripts\python.exe" -m pip install -r requirements.txt
            )
            if errorlevel 1 (
                echo [ERROR] Failed to install dependencies.
                goto :fail
            )
            echo [OK] Dependencies installed.
        ) else (
            echo [ERROR] requirements.txt not found.
            goto :fail
        )
    )
)
echo.

:: 4. Start the bot
echo [4/4] Starting Discord Music Bot...
echo.
".venv\Scripts\python.exe" main.py
set "BOT_EXIT=%errorlevel%"

echo.
echo Bot exited with code %BOT_EXIT%.
pause
exit /b %BOT_EXIT%

:fail
echo.
pause
exit /b 1

exit /b %BOT_EXIT%

:fail
echo.
pause
exit /b 1