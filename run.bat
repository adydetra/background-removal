@echo off
setlocal

set "VENV_DIR=.venv"

if exist "%VENV_DIR%\Scripts\activate.bat" (
    call "%VENV_DIR%\Scripts\activate.bat"
    echo [run] Virtual environment activated.
) else (
    echo [run] Virtual environment not found. Run setup.bat first.
    exit /b 1
)

echo [run] Launching python index.py ...
python index.py

endlocal
