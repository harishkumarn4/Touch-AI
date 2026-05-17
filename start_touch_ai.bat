@echo off
echo ===================================================
echo        Starting Touch AI Desktop Assistant
echo ===================================================

:: Set the API Key (Required for Google Lens Vision)
set GEMINI_API_KEY=AIzaSyCn2uqXd3FKweLpqDgP90evHKruXaeEeTo

:: Start the Backend in a new window
echo Starting Backend Engine...
start cmd /k "cd backend && .\venv\Scripts\activate && python app.py"

:: Start the Frontend in a new window
echo Starting Frontend UI...
start cmd /k "cd frontend && npm run dev"

echo.
echo Both engines are starting up! Please wait a few seconds...
echo You can close this small window now.
pause
