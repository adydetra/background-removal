@echo off
setlocal

set "VENV_DIR=.venv"

where uv >nul 2>&1
if %errorlevel%==0 (
    echo [setup] Creating virtual environment with uv...
    uv venv
    if %errorlevel% neq 0 (
        echo [setup] Failed to create virtual environment with uv.
        exit /b 1
    )

    call "%VENV_DIR%\Scripts\activate.bat"
    echo [setup] Installing dependencies via uv pip...
    uv pip install -r requirements.txt
) else (
    echo [setup] uv not found. Falling back to python -m venv and pip.
    python -m venv "%VENV_DIR%"
    if not exist "%VENV_DIR%\Scripts\activate.bat" (
        echo [setup] Failed to create virtual environment.
        exit /b 1
    )

    call "%VENV_DIR%\Scripts\activate.bat"
    echo [setup] Upgrading pip...
    python -m pip install --upgrade pip
    echo [setup] Installing dependencies via pip...
    pip install -r requirements.txt
)

echo [setup] Installation complete.
endlocal
exit /b 0
