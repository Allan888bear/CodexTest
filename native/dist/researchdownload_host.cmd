@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
set "HOST_SCRIPT=%SCRIPT_DIR%..\researchdownload_host.py"

if exist "%SYSTEMROOT%\py.exe" (
    set "PY_CMD=%SYSTEMROOT%\py.exe -3"
) else (
    where py >nul 2>nul
    if %errorlevel% equ 0 (
        set "PY_CMD=py -3"
    ) else (
        where python >nul 2>nul
        if %errorlevel% equ 0 (
            for /f "delims=" %%I in ('where python') do (
                set "PY_CMD=%%I"
                goto :run
            )
        ) else (
            echo Could not find a Python interpreter on PATH. >&2
            exit /b 9009
        )
    )
)

:run
if not exist "%HOST_SCRIPT%" (
    echo Unable to locate host script at %HOST_SCRIPT%. >&2
    exit /b 2
)

call %PY_CMD% "%HOST_SCRIPT%" %*
set "EXITCODE=%ERRORLEVEL%"
endlocal & exit /b %EXITCODE%
