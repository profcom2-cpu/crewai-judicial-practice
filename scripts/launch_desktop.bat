@echo off
setlocal
cd /d "%~dp0\.."
set PYTHONDONTWRITEBYTECODE=1
set PYTHONIOENCODING=utf-8
set CREWAI_TRACING_ENABLED=false
if not exist ".venv\Scripts\python.exe" (
  echo Нет .venv. Создайте окружение Python 3.12 и поставьте requirements.txt
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m practice_crew.webapp
if errorlevel 1 pause
