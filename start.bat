@echo off
REM Startup script for Financial Document Parser services

echo ================================================
echo  Financial Document Parser - Service Launcher
echo ================================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found!
    echo Please run: python -m venv venv
    echo Then run: venv\Scripts\activate
    echo And: pip install -r requirements.txt
    pause
    exit /b 1
)

echo Select which service to run:
echo.
echo 1. Flask API only
echo 2. Streamlit UI only
echo 3. Both (Flask API + Streamlit UI)
echo 4. Exit
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto flask
if "%choice%"=="2" goto streamlit
if "%choice%"=="3" goto both
if "%choice%"=="4" goto end

echo Invalid choice. Please run the script again.
pause
exit /b 1

:flask
echo.
echo Starting Flask API...
call venv\Scripts\activate.bat
python app.py
goto end

:streamlit
echo.
echo Starting Streamlit UI...
echo Note: Flask API must be running for the UI to work!
call venv\Scripts\activate.bat
streamlit run streamlit_app.py
goto end

:both
echo.
echo Starting Flask API in a new window...
start "Flask API" cmd /k "call venv\Scripts\activate.bat && python app.py"
timeout /t 3 /nobreak >nul
echo.
echo Starting Streamlit UI...
call venv\Scripts\activate.bat
streamlit run streamlit_app.py
goto end

:end
echo.
echo Exiting...
