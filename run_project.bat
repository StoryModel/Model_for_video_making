@echo off
title AI Manhwa Video Generator

echo ================================
echo Starting AI Manhwa Video Generator
echo ================================

echo Checking Python 3.11...
py -3.11 --version
if errorlevel 1 (
    echo Python 3.11 not found. Install Python 3.11 first.
    pause
    exit /b
)

echo Checking Node.js...
node -v
if errorlevel 1 (
    echo Node.js not found. Install Node.js LTS first.
    pause
    exit /b
)

echo Starting Backend...
start "Backend" cmd /k "cd /d %~dp0backend && py -3.11 -m uvicorn app:app --reload"

timeout /t 5 >nul

echo Starting Frontend...
start "Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

timeout /t 5 >nul
start http://localhost:5173

echo Project started.
echo Keep backend and frontend windows open.
pause
