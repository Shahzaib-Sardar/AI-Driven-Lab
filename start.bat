@echo off
cd /d "%~dp0"

echo Starting backend...
start "Backend" cmd /k ".\.venv\Scripts\Activate.bat && python backend\run.py"

timeout /t 1 >nul

echo Starting frontend...
start "Frontend" cmd /k "npm --prefix frontend run dev"

echo Servers started in separate windows. Close those windows to stop them.
