@echo off
chcp 65001 > nul
echo ============================================
echo         Weather_Sochi Installer
echo ============================================
echo.


python --version > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo Please install Python 3.11 or higher from python.org
    pause
    exit /b 1
)

:: Check Python version
python -c "import sys; assert sys.version_info >= (3,11)" > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3.11 or higher is required
    echo Current version:
    python --version
    pause
    exit /b 1
)

:: Create virtual environment
echo [INFO] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)

:: Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

:: Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip

:: Install requirements
echo [INFO] Installing requirements...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install requirements
    pause
    exit /b 1
)

echo.
echo ============================================
echo        Installation completed!
echo ============================================
echo You can now run the application using run.bat
pause