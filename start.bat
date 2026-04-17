@echo off
REM Shadow Engine Startup Script for Windows

echo.
echo 🚀 Shadow Engine Startup
echo ========================
echo.

REM Check Python version
echo ✓ Checking Python version...
python --version

REM Create virtual environment if not exists
if not exist "venv" (
    echo ✓ Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo ✓ Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo ✓ Installing dependencies...
pip install -r requirements.txt --quiet

REM Check Ollama connection
echo ✓ Checking Ollama connection...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:11434/api/tags' -ErrorAction SilentlyContinue; if ($response.StatusCode -eq 200) { Write-Host '  ✓ Ollama is running' } } catch { Write-Host '  ⚠️  Ollama not accessible at http://localhost:11434'; Write-Host '  Start Ollama: ollama serve'; Write-Host '  Pull model: ollama pull deepseek:13b' }"

REM Start application
echo.
echo ✓ Starting Shadow Engine...
echo   API: http://localhost:8000
echo   Docs: http://localhost:8000/docs
echo.

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
