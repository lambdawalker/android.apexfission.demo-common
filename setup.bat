@echo off
setlocal
where android-repo-setup.exe >nul 2>&1
if errorlevel 1 (
    echo Install android-repo-setup v0.1.4 from the tooling releases and add it to PATH. 1>&2
    exit /b 1
)
android-repo-setup.exe --project "%~dp0." %*
exit /b %ERRORLEVEL%
