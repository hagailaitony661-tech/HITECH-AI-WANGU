@echo off
setlocal
cd /d "%~dp0"
title HAGAI AI CLOUD - Local Server

echo ==========================================
echo       HAGAI AI CLOUD - WINDOWS STARTER
echo ==========================================
echo.

where py >nul 2>nul
if errorlevel 1 (
  echo Python haijapatikana. Sakinisha Python 3.11 au mpya, kisha jaribu tena.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo [1/4] Inaandaa mazingira ya Python...
  py -3 -m venv .venv
  if errorlevel 1 (
    echo Imeshindikana kutengeneza virtual environment.
    pause
    exit /b 1
  )
)

echo [2/4] Inaweka mahitaji ya backend...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  echo Imeshindikana kusakinisha dependencies. Kagua intaneti na nafasi ya diski.
  pause
  exit /b 1
)

echo [3/4] Inatengeneza API key ya muda kwa session hii...
for /f %%K in ('powershell -NoProfile -Command "[guid]::NewGuid().ToString(''N'') + [guid]::NewGuid().ToString(''N'')"') do set "HAGAI_API_KEY=%%K"
set "OLLAMA_BASE_URL=http://127.0.0.1:11434"
set "HAGAI_DATA_DIR=%~dp0data"

echo.
echo HIFADHI API KEY HII KWA SESSION HII:
echo %HAGAI_API_KEY%
echo.
echo [4/4] Inawasha HAGAI AI CLOUD...
echo Dashboard: http://127.0.0.1:8000
echo API docs:  http://127.0.0.1:8000/docs
echo.
echo Kwenye dashboard, fungua API & Muunganisho:
echo Backend URL: http://127.0.0.1:8000
echo API key: bandika key iliyoonyeshwa hapo juu.
echo.
echo Acha dirisha hili wazi wakati unatumia mfumo.
echo Bonyeza CTRL+C kusimamisha seva.
start "" http://127.0.0.1:8000
".venv\Scripts\python.exe" -m uvicorn main:app --host 127.0.0.1 --port 8000
pause
