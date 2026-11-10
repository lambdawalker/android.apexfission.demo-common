@echo off
setlocal DisableDelayedExpansion
set "CLI_VERSION=v0.1.4"
set "CLI_EXE=%~dp0bin\%CLI_VERSION%\android-repo-setup.exe"
if not exist "%CLI_EXE%" (
    powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "%~dp0scripts\install-setup-cli.ps1" -Version "%CLI_VERSION%"
    if errorlevel 1 exit /b 1
)
"%CLI_EXE%" --project "%~dp0." %*
exit /b %ERRORLEVEL%
