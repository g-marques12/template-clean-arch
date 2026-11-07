@echo off
setlocal
cd /d "%~dp0.."

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" "build\build_exe.py" %*
) else if exist "venv\Scripts\python.exe" (
    "venv\Scripts\python.exe" "build\build_exe.py" %*
) else (
    python "build\build_exe.py" %*
)

endlocal
