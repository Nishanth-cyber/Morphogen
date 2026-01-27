@echo off
echo ============================================
echo   Generative Design Studio - Starting...
echo ============================================
echo.

REM Check if virtual environment exists
if not exist "backend\venv" (
    echo ERROR: Virtual environment not found!
    echo Please run: cd backend ^&^& python -m venv venv
    echo Then: venv\Scripts\activate ^&^& pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment and start backend
echo [1/2] Starting Backend Server...
start cmd /k "cd backend && venv\Scripts\activate && python main.py"

timeout /t 3 /nobreak > nul

REM Start frontend
echo [2/2] Opening Frontend...
start cmd /k "cd frontend && python -m http.server 3000"

timeout /t 2 /nobreak > nul

echo.
echo ============================================
echo   Servers Started Successfully!
echo ============================================
echo.
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:3000
echo   API Docs: http://localhost:8000/docs
echo.
echo Opening browser...
start http://localhost:3000

echo.
echo Press any key to stop all servers...
pause > nul

REM Kill servers
taskkill /F /FI "WINDOWTITLE eq *backend*" /T > nul 2>&1
taskkill /F /FI "WINDOWTITLE eq *frontend*" /T > nul 2>&1

echo.
echo Servers stopped.
