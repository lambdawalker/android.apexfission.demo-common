@echo off
setlocal
where uv >nul 2>&1
if errorlevel 1 (
    echo Install uv and add it to PATH. 1>&2
    exit /b 1
)
uv run "%~dp0scripts\setup_demo_apk_signing.py" %*
exit /b %ERRORLEVEL%
