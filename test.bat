@echo off
echo Activate venv
set SCRIPT_DIR=%~dp0

call %SCRIPT_DIR%.venv\Scripts\activate.bat  :: Замена на путь к activate.bat
if %errorlevel% neq 0 (
    echo Error activate venv.
    pause
    exit /b 1
)
echo venv active.
echo script start...
python %SCRIPT_DIR%screen_generator.py  :: Скрипт
echo script contine.
@REM pause