@echo off
setlocal
cd /d %~dp0..

if not exist flask_app\.venv (
  python -m venv flask_app\.venv
)

call flask_app\.venv\Scripts\pip.exe install -r flask_app\requirements.txt
start "flask" cmd /c "flask_app\.venv\Scripts\python.exe flask_app\app.py"

timeout /t 3 >nul
start "" http://localhost:5000

endlocal
