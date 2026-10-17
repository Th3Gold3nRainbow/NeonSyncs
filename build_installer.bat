@echo off
setlocal
REM ============================================================
REM  build_installer.bat — a executer APRES build_exe.bat
REM  Compile installer.iss en un installeur Windows via Inno Setup.
REM ============================================================

set "ISCC="

if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" (
    set "ISCC=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
) else if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" (
    set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
) else if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" (
    set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
) else (
    where iscc >nul 2>nul
    if not errorlevel 1 set "ISCC=iscc"
)

if "%ISCC%"=="" (
    echo.
    echo ERREUR: Inno Setup 6 n'est pas trouve sur cette machine.
    echo Installez-le depuis https://jrsoftware.org/isdl.php
    echo puis relancez ce script, ou ouvrez installer.iss directement
    echo avec l'application Inno Setup Compiler.
    echo.
    pause
    exit /b 1
)

if not exist dist\NeonSyncs.exe (
    echo.
    echo ERREUR: dist\NeonSyncs.exe est introuvable.
    echo Executez d'abord build_exe.bat
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  Compilation de l'installeur NeonSyncs avec Inno Setup 6...
echo ============================================================
echo.

"%ISCC%" installer.iss
if errorlevel 1 (
    echo.
    echo ERREUR: la compilation Inno Setup a echoue.
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Installeur genere avec succes dans Output\NeonSyncs-Setup.exe
echo ============================================================
echo.
pause
